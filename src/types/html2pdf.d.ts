declare module 'html2pdf.js' {
  export default function html2pdf(): html2pdf.Html2PdfWrapper;
  
  namespace html2pdf {
    interface Html2PdfWrapper {
      from(element: HTMLElement | string): Html2PdfWrapper;
      set(options: any): Html2PdfWrapper;
      save(filename?: string): Promise<void>;
    }
  }
} 