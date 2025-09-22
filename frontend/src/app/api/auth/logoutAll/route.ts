// src/app/api/auth/logoutAll/route.ts
import { NextRequest, NextResponse } from "next/server";
import { verifyAccessToken } from "@/lib/auth/jwt";
import { revokeAllTokensForUser } from "@/lib/auth/refresh";

export async function POST(req: NextRequest) {
    try {
        const token = req.cookies.get("token")?.value;
        if (!token) {
            return NextResponse.json({ error: "Not authenticated" }, { status: 401 });
        }

        const decoded = verifyAccessToken<{ id: string }>(token);
        if (!decoded) {
            return NextResponse.json({ error: "Invalid token" }, { status: 401 });
        }

        await revokeAllTokensForUser(decoded.id);

        // Clear cookies
        const res = NextResponse.json({ success: true });
        res.cookies.set("token", "", { path: "/", maxAge: 0 });
        res.cookies.set("refresh_token", "", { path: "/", maxAge: 0 });
        return res;
    } catch (err) {
        console.error("LogoutAll error:", err);
        return NextResponse.json({ error: "Server error" }, { status: 500 });
    }
}
