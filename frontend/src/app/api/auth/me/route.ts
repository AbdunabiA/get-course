// src/app/api/auth/me/route.ts
import { NextResponse } from "next/server";
import prisma from "@/lib/prisma";
import { verifyAccessToken, signAccessToken } from "@/lib/auth/jwt";
import { verifyRefreshToken, rotateRefreshToken } from "@/lib/auth/refresh";

export async function GET(req: Request) {
    const accessToken = req.headers
        .get("cookie")
        ?.split("; ")
        .find((c) => c.startsWith("token="))
        ?.split("=")[1];

    const refreshToken = req.headers
        .get("cookie")
        ?.split("; ")
        .find((c) => c.startsWith("refreshToken="))
        ?.split("=")[1];

    // 1. Try access token
    if (accessToken) {
        const decoded = verifyAccessToken<{ id: string; role: string }>(accessToken);
        if (decoded) {
            const user = await prisma.user.findUnique({
                where: { id: decoded.id },
                select: { id: true, email: true, role: true },
            });
            if (user) return NextResponse.json(user);
        }
    }

    // 2. Try refresh token if available
    if (refreshToken) {
        const decodedRefresh = await verifyRefreshToken(refreshToken);
        if (decodedRefresh) {
            // ✅ Issue new access token
            const newAccessToken = signAccessToken({
                id: decodedRefresh.id,
                email: decodedRefresh.email,
                role: decodedRefresh.role,
            });

            // 🔄 Rotate refresh token (optional but recommended)
            const newRefreshToken = await rotateRefreshToken(decodedRefresh.id);

            const response = NextResponse.next();
            response.cookies.set("token", newAccessToken, {
                httpOnly: true,
                secure: process.env.NODE_ENV === "production",
                sameSite: "lax",
                maxAge: 60 * 15, // 15m
            });
            response.cookies.set("refreshToken", newRefreshToken, {
                httpOnly: true,
                secure: process.env.NODE_ENV === "production",
                sameSite: "lax",
                maxAge: 60 * 60 * 24 * 30, // 30d
            });

            // Return user info
            const user = await prisma.user.findUnique({
                where: { id: decodedRefresh.id },
                select: { id: true, email: true, role: true },
            });

            return NextResponse.json(user, { status: 200, headers: response.headers });
        }
    }

    // 3. If nothing works → unauthorized
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
}
