import { NextRequest, NextResponse } from "next/server";
import { findValidRefreshTokenByPlain, createRefreshToken } from "@/lib/auth/refresh";
import { signAccessToken } from "@/lib/auth/jwt";
import { prisma } from "@/lib/prisma";

export async function POST(req: NextRequest) {
    try {
        const refreshTokenCookie = req.cookies.get("refresh_token")?.value;
        if (!refreshTokenCookie) {
            return NextResponse.json({ error: "No refresh token" }, { status: 401 });
        }

        // 1. Look up refresh token
        const tokenRecord = await findValidRefreshTokenByPlain(refreshTokenCookie);
        if (!tokenRecord) {
            return NextResponse.json({ error: "Invalid or expired refresh token" }, { status: 401 });
        }

        // 2. Load user
        const user = await prisma.user.findUnique({ where: { id: tokenRecord.userId } });
        if (!user) {
            return NextResponse.json({ error: "User not found" }, { status: 404 });
        }

        // 3. Rotate refresh token (chain old → new)
        const { token: newRefresh } = await createRefreshToken(user.id, tokenRecord.id);

        // 4. Issue new access token
        const accessToken = signAccessToken({
            id: user.id,
            email: user.email,
            role: user.role,
        });

        // 5. Send cookies
        const res = NextResponse.json({ message: "Token refreshed" });

        res.cookies.set("token", accessToken, {
            httpOnly: true,
            secure: process.env.NODE_ENV === "production",
            sameSite: "strict",
            path: "/",
            maxAge: 60 * 15, // 15 minutes
        });

        res.cookies.set("refresh_token", newRefresh, {
            httpOnly: true,
            secure: process.env.NODE_ENV === "production",
            sameSite: "strict",
            path: "/api/auth/refresh", // only sent to this endpoint
            maxAge: 60 * 60 * 24 * 30, // 30 days
        });

        return res;
    } catch (err) {
        console.error("Refresh error:", err);
        return NextResponse.json({ error: "Server error" }, { status: 500 });
    }
}
