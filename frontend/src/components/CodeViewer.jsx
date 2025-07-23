/**
 * CodeViewer component for displaying generated Infrastructure as Code.
 * 
 * Uses Monaco Editor to provide syntax highlighting and a professional
 * code editing experience for the generated Terraform/CloudFormation code.
 */

 import React, { useRef } from 'react';
 import Editor from '@monaco-editor/react';
 import { Copy, Download, Code2, Loader2 } from 'lucide-react';
 import toast from 'react-hot-toast';
 import clsx from 'clsx';
 
 import useAppStore from '../store/appStore';
 
 const CodeViewer = () => {
   const { generatedCode, outputFormat, isGenerating } = useAppStore();
   const editorRef = useRef(null);
   
   /**
    * Determine the language for Monaco Editor based on output format.
    */
   const getEditorLanguage = () => {
     return outputFormat === 'terraform' ? 'hcl' : 'yaml';
   };
   
   /**
    * Copy code to clipboard.
    */
   const handleCopy = async () => {
     try {
       await navigator.clipboard.writeText(generatedCode);
       toast.success('Code copied to clipboard!');
     } catch (error) {
       toast.error('Failed to copy code');
     }
   };
   
   /**
    * Download code as a file.
    */
   const handleDownload = () => {
     const fileExtension = outputFormat === 'terraform' ? 'tf' : 'yaml';
     const fileName = `infrastructure.${fileExtension}`;
     
     const blob = new Blob([generatedCode], { type: 'text/plain' });
     const url = URL.createObjectURL(blob);
     
     const link = document.createElement('a');
     link.href = url;
     link.download = fileName;
     document.body.appendChild(link);
     link.click();
     document.body.removeChild(link);
     
     URL.revokeObjectURL(url);
     toast.success(`Downloaded ${fileName}`);
   };
   
   /**
    * Handle editor mount to store reference.
    */
   const handleEditorMount = (editor, monaco) => {
     editorRef.current = editor;
     
     // Configure HCL language for Terraform
     monaco.languages.register({ id: 'hcl' });
     monaco.languages.setMonarchTokensProvider('hcl', {
       tokenizer: {
         root: [
           [/[a-z_]\w*/, { cases: { '@keywords': 'keyword', '@default': 'identifier' } }],
           [/"([^"\\]|\\.)*"/, 'string'],
           [/\d+/, 'number'],
           [/#.*$/, 'comment'],
           [/\/\/.*$/, 'comment'],
           [/\/\*/, 'comment', '@comment'],
         ],
         comment: [
           [/[^\/*]+/, 'comment'],
           [/\*\//, 'comment', '@pop'],
           [/[\/*]/, 'comment'],
         ],
       },
       keywords: [
         'resource', 'data', 'variable', 'output', 'locals', 'module',
         'provider', 'terraform', 'backend', 'required_version', 'required_providers',
         'for_each', 'count', 'depends_on', 'lifecycle', 'true', 'false', 'null',
       ],
     });
   };
   
   if (!generatedCode && !isGenerating) {
     return null;
   }
   
   return (
     <div className="bg-white rounded-lg shadow-md overflow-hidden">
       {/* Header */}
       <div className="px-4 py-3 bg-gray-50 border-b border-gray-200 flex items-center justify-between">
         <div className="flex items-center gap-2">
           <Code2 className="w-5 h-5 text-gray-600" />
           <h3 className="font-medium text-gray-900">
             Generated {outputFormat === 'terraform' ? 'Terraform' : 'CloudFormation'} Code
           </h3>
         </div>
         
         {generatedCode && (
           <div className="flex items-center gap-2">
             <button
               onClick={handleCopy}
               className={clsx(
                 'flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium rounded-md transition-colors',
                 'text-gray-700 bg-white border border-gray-300',
                 'hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-1'
               )}
             >
               <Copy className="w-4 h-4" />
               Copy
             </button>
             
             <button
               onClick={handleDownload}
               className={clsx(
                 'flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium rounded-md transition-colors',
                 'text-white bg-primary border border-primary',
                 'hover:bg-primary-dark focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-1'
               )}
             >
               <Download className="w-4 h-4" />
               Download
             </button>
           </div>
         )}
       </div>
       
       {/* Editor Container */}
       <div className="monaco-editor-wrapper">
         {isGenerating ? (
           <div className="h-96 flex items-center justify-center bg-gray-50">
             <div className="text-center">
               <Loader2 className="w-12 h-12 text-primary animate-spin mx-auto mb-4" />
               <p className="text-gray-600">Generating Infrastructure as Code...</p>
               <p className="text-sm text-gray-500 mt-2">
                 Analyzing your diagram and creating {outputFormat} configuration
               </p>
             </div>
           </div>
         ) : (
           <Editor
             height="500px"
             language={getEditorLanguage()}
             value={generatedCode}
             onMount={handleEditorMount}
             theme="vs"
             options={{
               readOnly: true,
               minimap: { enabled: false },
               scrollBeyondLastLine: false,
               fontSize: 14,
               lineNumbers: 'on',
               renderLineHighlight: 'none',
               overviewRulerLanes: 0,
               hideCursorInOverviewRuler: true,
               overviewRulerBorder: false,
               scrollbar: {
                 vertical: 'visible',
                 horizontal: 'visible',
                 useShadows: false,
                 verticalScrollbarSize: 10,
                 horizontalScrollbarSize: 10,
               },
               padding: { top: 16, bottom: 16 },
             }}
           />
         )}
       </div>
     </div>
   );
 };
 
 export default CodeViewer;