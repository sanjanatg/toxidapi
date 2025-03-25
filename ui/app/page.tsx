import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import DemoInterface from "@/components/demo-interface"
import ApiDocs from "@/components/api-docs"
import SdkExamples from "@/components/sdk-examples"
import Features from "@/components/features"

export default function Home() {
  return (
    <main className="min-h-screen bg-white">
      <header className="bg-blue-600 text-white p-4 md:p-6">
        <div className="container mx-auto">
          <h1 className="text-3xl font-bold">ToxidAPI</h1>
          <p className="text-blue-100 mt-2">Advanced content moderation powered by Google&apos;s Gemini AI</p>
        </div>
      </header>

      <div className="container mx-auto p-4 md:p-6">
        <Tabs defaultValue="demo" className="w-full">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="demo">Demo</TabsTrigger>
            <TabsTrigger value="features">Features</TabsTrigger>
            <TabsTrigger value="docs">API Docs</TabsTrigger>
            <TabsTrigger value="sdk">SDK Examples</TabsTrigger>
          </TabsList>
          <TabsContent value="demo">
            <DemoInterface />
          </TabsContent>
          <TabsContent value="features">
            <Features />
          </TabsContent>
          <TabsContent value="docs">
            <ApiDocs />
          </TabsContent>
          <TabsContent value="sdk">
            <SdkExamples />
          </TabsContent>
        </Tabs>
      </div>

      <footer className="bg-gray-100 p-4 mt-8 border-t">
        <div className="container mx-auto text-center text-gray-600">
          <p>© {new Date().getFullYear()} ToxidAPI. All rights reserved.</p>
        </div>
      </footer>
    </main>
  )
}

