// Render the globe in software on machines where WebGL is disabled. At local
// scales a tangent plane is sufficient and the native 2D image path is faster.
export function createSoftwareRenderer({canvas, target, earthRadius, spans, images, mix, smooth}) {
  const fallback=document.createElement('canvas');fallback.id='earth';fallback.setAttribute('aria-label',canvas.getAttribute('aria-label'));
  canvas.replaceWith(fallback);
  const ctx=fallback.getContext('2d'), scratch=document.createElement('canvas'),sc=scratch.getContext('2d');
  let pixels, tw,th;
  return {
    load(img,i){
      if(i!==0)return;
      const tex=document.createElement('canvas');tw=tex.width=2048;th=tex.height=1024;
      const c=tex.getContext('2d');c.drawImage(img,0,0,tw,th);pixels=c.getImageData(0,0,tw,th).data;
    },
    draw(f){
      if(fallback.width!==f.w||fallback.height!==f.h){fallback.width=f.w;fallback.height=f.h;}
      ctx.clearRect(0,0,f.w,f.h);if(!pixels)return;
      const scale=f.r*Math.cos(target.lat)/earthRadius;
      const cover=2*Math.max(f.x,f.w-f.x,f.y,f.h-f.y,310);
      const local=Math.abs(f.lon-target.lon)<.001;
      const base=local?spans.findLastIndex((span,i)=>images[i+1]&&scale*span>=cover):-1;
      if(base<0){
        const coarse=Math.min(1,540/f.w), w=Math.max(1,Math.round(f.w*coarse)), h=Math.max(1,Math.round(f.h*coarse));
        if(scratch.width!==w||scratch.height!==h){scratch.width=w;scratch.height=h;}
        const data=sc.createImageData(w,h),out=data.data,sl=Math.sin(f.lat),cl=Math.cos(f.lat);
        for(let y=0;y<h;y++)for(let x=0;x<w;x++){
          const east=(x/coarse-f.x)/f.r,north=(f.y-y/coarse)/f.r,z2=1-east*east-north*north;
          if(z2<0)continue;
          const z=Math.sqrt(z2),lat=Math.asin(north*cl+z*sl),lon=f.lon+Math.atan2(east,z*cl-north*sl);
          const px=(Math.floor((.5+lon/(2*Math.PI))*tw)%tw+tw)%tw,py=Math.min(th-1,Math.max(0,Math.floor((.5-lat/Math.PI)*th)));
          const src=(py*tw+px)*4,dst=(y*w+x)*4,light=mix(.52+.49*Math.max(0,-.6*east+.47*north+.85*z),1,f.fade);
          for(let j=0;j<3;j++)out[dst+j]=pixels[src+j]*light;
          out[dst+3]=255;
        }
        sc.putImageData(data,0,0);ctx.drawImage(scratch,0,0,f.w,f.h);
      }
      if(!local)return;
      spans.forEach((span,i)=>{
        const size=scale*span;
        if(i<base||!images[i+1]||size<160)return;
        ctx.globalAlpha=smooth((size-160)/450);ctx.drawImage(images[i+1],f.x-size/2,f.y-size/2,size,size);
      });
      ctx.globalAlpha=1;
    }
  };
}
