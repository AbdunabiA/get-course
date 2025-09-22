import { NextResponse } from "next/server";
import prisma from "@/lib/prisma";
import { hashPassword } from "@/lib/auth/password";
import cookie from "cookie";
import { signAccessToken } from "@/lib/auth/jwt";
import { createRefreshToken } from "@/lib/auth/refresh";

export async function POST(req: Request) {
    try {
        const { email, password, name } = await req.json();

        if (!email || !password || !name) {
            return NextResponse.json({ error: "Missing fields" }, { status: 400 });
        }

        // 1. Check if user already exists
        const existingUser = await prisma.user.findUnique({ where: { email } });
        if (existingUser) {
            return NextResponse.json({ error: "User already exists" }, { status: 400 });
        }

        // 2. Hash password
        const hashedPassword = await hashPassword(password);

        // 3. Create user with default role STUDENT
        const user = await prisma.user.create({
            data: {
                email,
                password: hashedPassword,
                role: "STUDENT",
                profile: { create: { name } },
            },
        });

        // 4. Create tokens
        const accessToken = signAccessToken({ id: user.id, email: user.email, role: user.role });
        const { token: refreshToken } = await createRefreshToken(user.id);

        // 5. Response with cookies
        const res = NextResponse.json({ message: "User registered successfully" });

        // Access token cookie (short-lived, e.g. 15m)
        res.headers.append(
            "Set-Cookie",
            cookie.serialize("token", accessToken, {
                httpOnly: true,
                secure: process.env.NODE_ENV === "production",
                sameSite: "strict",
                path: "/",
                maxAge: 60 * 15, // 15 minutes
            })
        );

        // Refresh token cookie (long-lived, e.g. 30d)
        res.headers.append(
            "Set-Cookie",
            cookie.serialize("refresh_token", refreshToken, {
                httpOnly: true,
                secure: process.env.NODE_ENV === "production",
                sameSite: "strict",
                path: "/api/auth/refresh", // refresh only sent where needed
                maxAge: 60 * 60 * 24 * 30, // 30 days
            })
        );

        return res;
    } catch (err) {
        console.error("Register error:", err);
        return NextResponse.json({ error: "Something went wrong" }, { status: 500 });
    }
}
