import { NextRequest, NextResponse } from "next/server"

const API_BASE = "https://get-course.onrender.com"

async function proxyRequest(req: NextRequest, path: string[]) {
    const url = `${API_BASE}/${path.join("/")}`

    const cookie = req.headers.get("cookie") ?? ""

    const backendRes = await fetch(url, {
        method: req.method,
        headers: {
            "Content-Type": req.headers.get("content-type") || "application/json",
            cookie,
        },
        body: req.method !== "GET" ? await req.text() : undefined,
    })

    const text = await backendRes.text()

    const res = new NextResponse(text, {
        status: backendRes.status,
    })

    const contentType = backendRes.headers.get("content-type")
    if (contentType) {
        res.headers.set("content-type", contentType)
    }

    const setCookie = backendRes.headers.get("set-cookie")
    if (setCookie) {
        res.headers.set("set-cookie", setCookie)
    }

    return res
}

// --- Route Handlers ---

export async function GET(req: NextRequest, context: { params: Promise<{ path: string[] }> }) {
    const params = await context.params
    return proxyRequest(req, params.path)
}

export async function POST(req: NextRequest, context: { params: Promise<{ path: string[] }> }) {
    const params = await context.params
    return proxyRequest(req, params.path)
}
