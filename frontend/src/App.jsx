/**
 * Main App component for Arch-I-Tect.
 * 
 * Orchestrates the entire application flow from image upload
 * to Infrastructure as Code generation.
 */

 import React, { useEffect } from 'react';
 import { Toaster } from 'react-hot-toast';
 import { Code2, Github, Info } from 'lucide-react';
 
 import UploadZone from './components/UploadZone';
 import ImagePreview from './components/ImagePreview';
 import GenerateControls from './components/GenerateControls';
 import CodeViewer from './components/CodeViewer';
 import FeedbackPanel from './components/FeedbackPanel';
 import useAppStore from './store/appStore';
 import { healthCheck } from './services/api';
 
 function App() {
   const { hasImage, error, clearError } = useAppStore();
   
   /**
    * Check backend health on mount.
    */
   useEffect(() => {
     const checkBackend = async () => {
       const isHealthy = await healthCheck();
       if (!isHealthy) {
         console.warn('Backend health check failed');
       }
     };
     
     checkBackend();
   }, []);
   
   return (
     <div className="min-h-screen bg-background">
       {/* Header */}
       <header className="bg-white shadow-sm border-b border-gray-200">
         <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
           <div className="flex items-center justify-between h-16">
             <div className="flex items-center gap-3">
               <div className="flex items-center justify-center w-10 h-10 bg-primary rounded-lg">
                 <Code2 className="w-6 h-6 text-white" />
               </div>
               <div>
                 <h1 className="text-xl font-bold text-gray-900">Arch-I-Tect</h1>
                 <p className="text-xs text-gray-600">Cloud Diagram to Code Generator</p>
               </div>
             </div>
             
             <a
               href="https://github.com/yourusername/arch-i-tect"
               target="_blank"
               rel="noopener noreferrer"
               className="flex items-center gap-2 px-4 py-2 text-sm text-gray-700 hover:text-gray-900 hover:bg-gray-50 rounded-lg transition-colors"
             >
               <Github className="w-4 h-4" />
               <span className="hidden sm:inline">View on GitHub</span>
             </a>
           </div>
         </div>
       </header>
       
       {/* Main Content */}
       <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
         {/* Error Alert */}
         {error && (
           <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
             <Info className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
             <div className="flex-1">
               <p className="text-sm text-red-800">{error}</p>
             </div>
             <button
               onClick={clearError}
               className="text-red-600 hover:text-red-800 text-sm font-medium"
             >
               Dismiss
             </button>
           </div>
         )}
         
         <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
           {/* Left Column - Upload and Controls */}
           <div className="lg:col-span-1 space-y-6">
             {/* Upload Section */}
             <div>
               <h2 className="text-lg font-semibold text-gray-900 mb-4">
                 1. Upload Architecture Diagram
               </h2>
               {hasImage() ? <ImagePreview /> : <UploadZone />}
             </div>
             
             {/* Generation Controls */}
             {hasImage() && (
               <div>
                 <h2 className="text-lg font-semibold text-gray-900 mb-4">
                   2. Configure Generation
                 </h2>
                 <GenerateControls />
               </div>
             )}
           </div>
           
           {/* Right Column - Results */}
           <div className="lg:col-span-2 space-y-6">
             {/* Generated Code */}
             <div>
               <h2 className="text-lg font-semibold text-gray-900 mb-4">
                 3. Generated Infrastructure Code
               </h2>
               <CodeViewer />
               
               {!hasImage() && (
                 <div className="bg-gray-50 border-2 border-dashed border-gray-300 rounded-lg p-12 text-center">
                   <Code2 className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                   <p className="text-gray-600 mb-2">No code generated yet</p>
                   <p className="text-sm text-gray-500">
                     Upload an architecture diagram to get started
                   </p>
                 </div>
               )}
             </div>
             
             {/* Feedback Panel */}
             <FeedbackPanel />
           </div>
         </div>
         
         {/* Features Section */}
         <div className="mt-16 pt-16 border-t border-gray-200">
           <h3 className="text-lg font-semibold text-gray-900 mb-6 text-center">
             How It Works
           </h3>
           
           <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
             <div className="text-center">
               <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
                 <span className="text-2xl font-bold text-primary">1</span>
               </div>
               <h4 className="font-medium text-gray-900 mb-2">Upload Diagram</h4>
               <p className="text-sm text-gray-600">
                 Drop your cloud architecture diagram - screenshots, draw.io exports, or whiteboard photos
               </p>
             </div>
             
             <div className="text-center">
               <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
                 <span className="text-2xl font-bold text-primary">2</span>
               </div>
               <h4 className="font-medium text-gray-900 mb-2">AI Analysis</h4>
               <p className="text-sm text-gray-600">
                 Our AI analyzes your diagram to identify cloud resources and their relationships
               </p>
             </div>
             
             <div className="text-center">
               <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
                 <span className="text-2xl font-bold text-primary">3</span>
               </div>
               <h4 className="font-medium text-gray-900 mb-2">Get IaC Code</h4>
               <p className="text-sm text-gray-600">
                 Receive production-ready Terraform or CloudFormation code ready to deploy
               </p>
             </div>
           </div>
         </div>
       </main>
       
       {/* Toast Container */}
       <Toaster
         position="bottom-right"
         toastOptions={{
           duration: 4000,
           style: {
             background: '#363636',
             color: '#fff',
           },
           success: {
             iconTheme: {
               primary: '#10B981',
               secondary: '#fff',
             },
           },
           error: {
             iconTheme: {
               primary: '#EF4444',
               secondary: '#fff',
             },
           },
         }}
       />
     </div>
   );
 }
 
 export default App;