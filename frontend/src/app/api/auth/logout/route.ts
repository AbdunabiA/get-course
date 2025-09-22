// src/app/api/auth/logout/route.ts
import { NextRequest, NextResponse } from "next/server";
import { findValidRefreshTokenByPlain, revokeTokenById } from "@/lib/auth/refresh";

export async function POST(req: NextRequest) {
    try {
        const refreshToken = req.cookies.get("refresh_token")?.value;
        if (refreshToken) {
            const record = await findValidRefreshTokenByPlain(refreshToken);
            if (record) {
                await revokeTokenById(record.id);
            }
        }

        // Clear cookies
        const res = NextResponse.json({ success: true });
        res.cookies.set("token", "", { path: "/", maxAge: 0 });
        res.cookies.set("refresh_token", "", { path: "/", maxAge: 0 });
        return res;
    } catch (err) {
        console.error("Logout error:", err);
        return NextResponse.json({ error: "Server error" }, { status: 500 });
    }
}
