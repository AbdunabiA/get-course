import { NextRequest, NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";
import { signAccessToken } from "@/lib/auth/jwt";
import { createRefreshToken } from "@/lib/auth/refresh";
import { verifyPassword } from "@/lib/auth/password";

export async function POST(req: NextRequest) {
    try {
        const { email, password } = await req.json();

        // 1. Find user
        const user = await prisma.user.findUnique({ where: { email } });
        if (!user) {
            return NextResponse.json({ error: "Invalid credentials" }, { status: 401 });
        }

        // 2. Verify password
        const valid = await verifyPassword(password, user.password);
        if (!valid) {
            return NextResponse.json({ error: "Invalid credentials" }, { status: 401 });
        }

        // 3. Generate tokens
        const accessToken = signAccessToken({
            id: user.id,
            role: user.role,
            email: user.email,
        });

        const { token: refreshToken } = await createRefreshToken(user.id);

        // 4. Response with cookies
        const res = NextResponse.json({ message: "Login successful" });

        // Access token cookie (short-lived)
        res.cookies.set("token", accessToken, {
            httpOnly: true,
            secure: process.env.NODE_ENV === "production",
            sameSite: "strict",
            path: "/",
            maxAge: 60 * 15, // 15 minutes
        });

        // Refresh token cookie (long-lived, only sent to refresh endpoint)
        res.cookies.set("refresh_token", refreshToken, {
            httpOnly: true,
            secure: process.env.NODE_ENV === "production",
            sameSite: "strict",
            path: "/api/auth/refresh",
            maxAge: 60 * 60 * 24 * 30, // 30 days
        });

        return res;
    } catch (err) {
        console.error("Login error:", err);
        return NextResponse.json({ error: "Server error" }, { status: 500 });
    }
}
