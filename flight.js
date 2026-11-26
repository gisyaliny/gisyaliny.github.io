'use strict';
(() => {
  const view = document.querySelector('.stage');
  const canvas = document.getElementById('earth');
  const route = document.getElementById('flight');
  const jump = document.getElementById('jump');
  const rad = Math.PI / 180, earthRadius = 6378137;
  const target = {lat: 39.63601 * rad, lon: -79.95535 * rad};
  const spans = [2000000, 480000, 110000, 26000, 6000, 1400, 700];
  const urls = ['imagery/earth-2k.webp', ...spans.map(span => 'imagery/wv-' + span + '.webp')];
  const clamp = n => Math.min(1, Math.max(0, n));
  const smooth = n => { const t = clamp(n); return t*t*(3-2*t); };
  const mix = (a,b,t) => a + (b-a)*t;
  const merc = lat => Math.log(Math.tan(Math.PI/4+lat/2));
  const landingSpan = 1050; // Width of the final view in Web Mercator meters.
  const campus = document.getElementById('campus-aerial');
  const overscan = 1.32;
  let campusView = '', campusTimer, campusFailed = false;

  function updateCampus(progress, zoomFraction, mobile) {
    if (progress < .80) {
      campus.style.opacity = '0';
      if (campusFailed) campusView = '';
      return;
    }
    const width = view.clientWidth, height = view.clientHeight;
    const anchorX = mobile ? .5 : .67, anchorY = mobile ? .65 : .51;
    const density = Math.min(2, devicePixelRatio || 1, 3072 / (overscan * Math.max(width, height)));
    const cols = Math.round(width * overscan * density), rows = Math.round(height * overscan * density);
    const key = [cols, rows, mobile].join('/');
    if (key !== campusView) {
      campusView = key;
      campusFailed = false;
      campus.hidden = true;
      clearTimeout(campusTimer);
      // Wait for resizing to settle before asking the county service for a new extent.
      campusTimer = setTimeout(() => {
        const dx = landingSpan * overscan, dy = dx * rows / cols;
        const west = earthRadius * target.lon - anchorX * dx;
        const north = earthRadius * merc(target.lat) + anchorY * dy;
        const bbox = [west, north - dy, west + dx, north].map(n => n.toFixed(3)).join(',');
        const params = new URLSearchParams({bbox, bboxSR:'3857', imageSR:'3857', size:cols + ',' + rows,
          layers:'show:1', format:'jpg', f:'image'});
        campus.onload = () => { if (campusView === key) { campus.hidden = false; schedule(); } };
        campus.onerror = () => { if (campusView === key) { campus.hidden = true; campusFailed = true; } };
        campus.src = 'https://services.wvgis.wvu.edu/arcgis/rest/services/Imagery_BaseMaps_EarthCover/wv_imagery_WVGISTC_leaf_off_mosaic/MapServer/export?' + params;
      }, 150);
    }
    campus.style.transformOrigin = (anchorX * 100) + '% ' + (anchorY * 100) + '%';
    campus.style.transform = 'scale(' + (overscan * zoomFraction) + ')';
    campus.style.opacity = String(smooth((zoomFraction - 1 / overscan) / .20));
  }
  const images = [];
  let pending = 0, previousStop = -1;

  // Only the imagery inside each georeferenced footprint is sampled. Adjacent
  // resolutions overlap, keeping a feature in place as its fine detail appears.
  function createGl() {
    const gl = canvas.getContext('webgl', {alpha:true, antialias:false, depth:false, premultipliedAlpha:false});
    if (!gl) return null;
    const program = gl.createProgram();
    function compile(type, source) {
      const shader = gl.createShader(type);
      gl.shaderSource(shader, source); gl.compileShader(shader);
      if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) throw Error(gl.getShaderInfoLog(shader));
      gl.attachShader(program, shader);
    }
    compile(gl.VERTEX_SHADER, 'attribute vec2 point; void main(){gl_Position=vec4(point,0.,1.);}');
    const declarations = urls.map((_,i) => 'uniform sampler2D layer'+i+';').join('\n');
    const samples = spans.map((span,i) => 'color=blendLayer(color,layer'+(i+1)+',offset,'+span+'.0,ready['+(i+1)+']);').join('\n');
    compile(gl.FRAGMENT_SHADER, `precision highp float;
      uniform vec2 dimensions,center,angles,dest;
      uniform float radius,fade,ready[8];
      ${declarations}
      const float pi=3.141592653589793;
      vec3 blendLayer(vec3 c,sampler2D tex,vec2 delta,float span,float loaded){
        vec2 uv=0.5+vec2(delta.x,-delta.y)/span;
        float edge=min(min(uv.x,1.-uv.x),min(uv.y,1.-uv.y));
        float weight=smoothstep(0.,.11,edge)*smoothstep(140.,540.,radius*.77*span/6378137.)*loaded;
        if(weight>.001)c=mix(c,texture2D(tex,clamp(uv,0.,1.)).rgb,weight);
        return c;
      }
      void main(){
        vec2 pixel=vec2(gl_FragCoord.x,dimensions.y-gl_FragCoord.y);
        vec2 q=(pixel-center)/radius;q.y=-q.y;
        float d=length(q);
        if(d>=1.){
          float halo=exp(-min(80.,(d-1.)*43.))*.43*(1.-fade);
          gl_FragColor=vec4(.30,.68,.84,halo);return;
        }
        float z=sqrt(max(0.,1.-d*d)),sl=sin(angles.y),cl=cos(angles.y);
        float lat=asin(clamp(q.y*cl+z*sl,-1.,1.));
        float lon=angles.x+atan(q.x,z*cl-q.y*sl);
        vec3 color=texture2D(layer0,vec2(fract(.5+lon/(2.*pi)),.5-lat/pi)).rgb;
        if(radius>585.){
          vec2 offset=6378137.*vec2(lon-dest.x,log(tan(pi*.25+lat*.5))-dest.y);
          ${samples}
        }
        float sun=dot(vec3(q,z),normalize(vec3(-.60,.47,.85)));
        color*=mix(.50+.56*max(0.,sun),1.,fade);
        color+=vec3(.15,.42,.56)*pow(1.-z,4.)*(1.-fade);
        gl_FragColor=vec4(color,1.);
      }`);
    gl.linkProgram(program);
    if (!gl.getProgramParameter(program,gl.LINK_STATUS)) throw Error(gl.getProgramInfoLog(program));
    gl.useProgram(program);
    const buffer=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,buffer);
    gl.bufferData(gl.ARRAY_BUFFER,new Float32Array([-1,-1,3,-1,-1,3]),gl.STATIC_DRAW);
    const pos=gl.getAttribLocation(program,'point');gl.enableVertexAttribArray(pos);gl.vertexAttribPointer(pos,2,gl.FLOAT,false,0,0);
    const u=Object.fromEntries(['dimensions','center','angles','radius','dest','fade','ready[0]'].map(n=>[n,gl.getUniformLocation(program,n)]));
    gl.uniform2f(u.dest,target.lon,merc(target.lat));
    const ready=new Float32Array(8);
    const textures=urls.map((_,i)=>{
      const texture=gl.createTexture();gl.activeTexture(gl.TEXTURE0+i);gl.bindTexture(gl.TEXTURE_2D,texture);
      gl.texImage2D(gl.TEXTURE_2D,0,gl.RGBA,1,1,0,gl.RGBA,gl.UNSIGNED_BYTE,new Uint8Array([8,27,43,255]));
      for(const key of [gl.TEXTURE_WRAP_S,gl.TEXTURE_WRAP_T])gl.texParameteri(gl.TEXTURE_2D,key,gl.CLAMP_TO_EDGE);
      for(const key of [gl.TEXTURE_MAG_FILTER,gl.TEXTURE_MIN_FILTER])gl.texParameteri(gl.TEXTURE_2D,key,gl.LINEAR);
      gl.uniform1i(gl.getUniformLocation(program,'layer'+i),i);return texture;
    });
    return {
      load(img,i){
        gl.activeTexture(gl.TEXTURE0+i);gl.bindTexture(gl.TEXTURE_2D,textures[i]);
        gl.texImage2D(gl.TEXTURE_2D,0,gl.RGBA,gl.RGBA,gl.UNSIGNED_BYTE,img);
        if((img.width&(img.width-1))===0&&(img.height&(img.height-1))===0){
          gl.generateMipmap(gl.TEXTURE_2D);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,gl.LINEAR_MIPMAP_LINEAR);
        }
        ready[i]=1;
      },
      draw(f){
        gl.viewport(0,0,f.w,f.h);gl.uniform2f(u.dimensions,f.w,f.h);gl.uniform2f(u.center,f.x,f.y);
        gl.uniform2f(u.angles,f.lon,f.lat);gl.uniform1f(u.radius,f.r);gl.uniform1f(u.fade,f.fade);
        gl.uniform1fv(u['ready[0]'],ready);gl.drawArrays(gl.TRIANGLES,0,3);
      }
    };
  }

  let renderer;
  try {renderer=createGl();} catch(error){console.warn('Using software globe',error);}
  async function useSoftwareRenderer() {
    renderer = null;
    const {createSoftwareRenderer} = await import('./flight-software.js');
    renderer = createSoftwareRenderer({canvas, target, earthRadius, spans, images, mix, smooth});
    images.forEach((img, i) => renderer.load(img, i));
    lastFrame = '';
    schedule();
  }
  if (renderer) {
    canvas.addEventListener('webglcontextlost', event => {
      event.preventDefault();
      useSoftwareRenderer();
    }, {once:true});
  } else {
    useSoftwareRenderer();
  }
  const requested=new Set();
  function loadLayer(i){
    if(requested.has(i))return;
    requested.add(i);
    const picture = document.createElement('picture');
    const source = document.createElement('source');
    source.type = 'image/avif';
    source.srcset = urls[i].replace('.webp', '.avif');
    const im = new Image();
    picture.append(source, im);
    im.onload = () => {
      images[i] = im;
      renderer?.load(im, i);
      schedule();
    };
    im.onerror = () => { if (source.parentNode) source.remove(); };
    im.src = urls[i];
  }
  loadLayer(0);
  // Use the opening HTML as the source when the flight returns to China.
  const caption = ['role','headline','sub','proof'].map(id => document.getElementById(id));
  const stops=[
    [caption[0].textContent, caption[1].innerHTML, caption[2].textContent, caption[3].textContent, caption[3].getAttribute('href')],
    ['Geography · New York to Texas','Across the Pacific','I crossed an ocean to study how the places we call home shape the lives we lead.','My background','#about'],
    ['GIS · Earth observation','From maps to code','I want what we learn from orbit to find its way into someone’s hands.','Explore my GeoAI work','#prithvi'],
    ['West Virginia GIS Technical Center','What floods here?','In West Virginia, I build tools to help communities see where water could reach, long before it rises.','Explore my flood-risk work','#wvfrf']
  ];
  const chapters=Array.from(document.querySelectorAll('#chapters button'));
  const origin=document.getElementById('origin');
  const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');
  const trail = document.getElementById('flight-trail');
  const ribbon = trail.querySelector('path'), spark = trail.querySelector('g');
  const gold = document.getElementById('trail-gold');
  const pin = document.getElementById('pin');
  function cameraRadius(progress, first, final) {
    const zoom = clamp((progress-.10)/.90);
    return first*Math.pow(final/first,zoom*zoom*(2-zoom));
  }
  function trailLocation(progress, first, final, approachRadius) {
    if (progress < .36) {
      const turn = smooth(progress/.36), t = turn + .09*Math.sin(Math.PI*turn);
      return {lat:mix(35*rad,target.lat+.10,t)+.39*Math.sin(Math.PI*t),
        lon:mix(104*rad,target.lon+2*Math.PI-.20,t)};
    }
    // Narrow the geographic approach with the camera, meeting the same campus coordinate at full zoom.
    const t = clamp((progress-.36)/.64);
    const scale = (1-smooth(t))*approachRadius/cameraRadius(progress,first,final);
    return {lat:target.lat+scale*(.10+.06*Math.sin(2*Math.PI*t)),
      lon:target.lon+scale*(-.20+.12*Math.sin(Math.PI*t))};
  }
  let head = 0, tail = 0, lastMove = 0, fadeTimer;
  function drawTrail(progress, lon, lat, x, y, radius, first, final) {
    const next = progress;
    const landing = smooth((progress-.945)/.055);
    pin.hidden = reducedMotion.matches ? progress<.88 : landing===0;
    pin.style.opacity = reducedMotion.matches ? 1 : landing;
    pin.style.transformOrigin = '0 0';
    pin.style.transform = reducedMotion.matches ? '' : 'scale('+mix(.22,1,landing)+')';
    if (progress === 0 || landing===1 || reducedMotion.matches) {
      trail.setAttribute('hidden', '');
      trail.classList.remove('tracing');
      head = tail = next;
      return;
    }
    const travel = next - head;
    if (travel) {
      const now = performance.now();
      // A fixed time lag translates to a longer geographic arc at higher speeds.
      const lag = Math.sign(travel) === Math.sign(head-tail)
        ? (head-tail) * Math.exp(-(now-lastMove)/260) : 0;
      tail = next - Math.sign(travel) * Math.min(.085, Math.abs(travel + lag));
      head = next;
      lastMove = now;
      clearTimeout(fadeTimer);
      trail.removeAttribute('hidden');
      trail.classList.add('tracing');
      fadeTimer = setTimeout(() => trail.classList.remove('tracing'), 95);
    }
    if (tail === head || performance.now()-lastMove > 1100) return;
    const cosLat = Math.cos(lat), sinLat = Math.sin(lat);
    const approachRadius = cameraRadius(.36,first,final);
    const points = Array.from({length:25}, (_, i) => {
      const location = trailLocation(mix(tail,head,i/24),first,final,approachRadius);
      const phi = location.lat, east = location.lon-lon;
      return {x:x + radius*Math.cos(phi)*Math.sin(east),
        y:y - radius*(cosLat*Math.sin(phi) - sinLat*Math.cos(phi)*Math.cos(east))};
    });
    const left = [], right = [];
    points.forEach((point, i) => {
      const before = points[Math.max(0,i-1)], after = points[Math.min(24,i+1)];
      const dx = after.x-before.x, dy = after.y-before.y;
      const halfWidth = 2.3*(i/24) / Math.max(.001,Math.hypot(dx,dy));
      left.push((point.x-dy*halfWidth).toFixed(2)+','+(point.y+dx*halfWidth).toFixed(2));
      right.push((point.x+dy*halfWidth).toFixed(2)+','+(point.y-dx*halfWidth).toFixed(2));
    });
    ribbon.setAttribute('d','M'+left.concat(right.reverse()).join(' L')+' Z');
    ribbon.style.opacity = spark.style.opacity = 1-landing;
    const start = points[0], tip = points[24];
    gold.setAttribute('x1',start.x); gold.setAttribute('y1',start.y);
    gold.setAttribute('x2',tip.x); gold.setAttribute('y2',tip.y);
    spark.setAttribute('transform','translate('+tip.x+' '+tip.y+')');
  }
  let captionAnimations = [];
  async function changeCaption(stop, previous) {
    const [role, title, sub, label, href] = stops[stop];
    const direction = previous <= stop ? 1 : -1;
    captionAnimations.forEach(animation => animation.cancel());
    if (!reducedMotion.matches && previous >= 0) {
      captionAnimations = caption.map(el => el.animate([
        {opacity:1, transform:'translateX(0)'},
        {opacity:0, transform:'translateX(' + (-22 * direction) + 'px)'}
      ], {duration:125, easing:'ease-in', fill:'forwards'}));
      await Promise.allSettled(captionAnimations.map(animation => animation.finished));
      if (stop !== previousStop) return;
      captionAnimations.forEach(animation => animation.cancel());
    }
    caption[0].textContent = role;
    caption[1].innerHTML = title;
    caption[2].textContent = sub;
    caption[3].href = href;
    caption[3].textContent = label;
    view.dataset.step = stop;
    if (!reducedMotion.matches) {
      captionAnimations = caption.map((el,i) => el.animate([
        {opacity:0, transform:'translateX(' + (direction * (32+i*6)) + 'px)'},
        {opacity:1, transform:'translateX(0)'}
      ], {duration:420, delay:i*35, easing:'cubic-bezier(.16,.8,.25,1)', fill:'backwards'}));
    }
  }
  let lastFrame='';
  function render(){
    pending=0;
    const bounds=route.getBoundingClientRect();
    if(bounds.bottom<=0)return;
    const p=clamp(-bounds.top/Math.max(1,route.offsetHeight-view.clientHeight));
    const mobile=view.clientWidth<=700, ratio=Math.min(devicePixelRatio||1,1.35,1600/view.clientWidth);
    const w=Math.round(view.clientWidth*ratio),h=Math.round(view.clientHeight*ratio);
    if(canvas.width!==w||canvas.height!==h){canvas.width=w;canvas.height=h;}
    const turn=smooth(p/.36);
    const first=Math.min(w*(mobile?.43:.285),h*(mobile?.245:.385));
    const final=earthRadius*w/(landingSpan*Math.cos(target.lat));
    const r=cameraRadius(p,first,final);
    // Start over China and turn east across the Pacific. -255° is 105° E.
    const lon=mix(-255*rad,target.lon,turn),lat=mix(33*rad,target.lat,turn)+.24*Math.sin(Math.PI*turn);
    const x=w*(mobile?.5:.67),y=h*(mobile?.65:.51);
    updateCampus(p,r/final,mobile);
    if(p>.08){
      const projected=spans.map(span=>r*Math.cos(target.lat)*span/earthRadius);
      const coarsest=projected.findLastIndex(size=>size>3*Math.max(w,h));
      projected.forEach((size,i)=>{if(i>=coarsest&&size>55)loadLayer(i+1);});
    }
    const key=[p,w,h,images.filter(Boolean).length].join('/');
    if(renderer && key!==lastFrame){
      renderer.draw({w,h,r,x,y,lon,lat,fade:smooth((p-.24)/.22)});
      lastFrame=key;
    }
    drawTrail(p,lon,lat,x/ratio,y/ratio,r/ratio,first,final);
    origin.hidden=reducedMotion.matches?p>.06:p>0;
    if(!origin.hidden){
      const phi=35*rad, delta=104*rad-lon;
      origin.style.left=(x+r*Math.cos(phi)*Math.sin(delta))/w*100+'%';
      origin.style.top=(y-r*(Math.cos(lat)*Math.sin(phi)-Math.sin(lat)*Math.cos(phi)*Math.cos(delta)))/h*100+'%';
    }
    const stop=p<.21?0:p<.53?1:p<.84?2:3;
    if(stop!==previousStop){
      const previous=previousStop;
      previousStop=stop;
      changeCaption(stop,previous);
      chapters[0].parentElement.style.setProperty('--chapter-index', stop);
      chapters.forEach((tab,i)=>i===stop?tab.setAttribute('aria-current','step'):tab.removeAttribute('aria-current'));
      document.getElementById('jump-label').textContent=stop===3?'Back to first light':'Follow the current';
      document.getElementById('arrow').textContent=stop===3?'↑':'↓';
    }
    view.style.setProperty('--p',p);view.style.setProperty('--shadow',mix(.05,.90,smooth((p-.19)/.30)));
  }
  function schedule(){if(!pending)pending=requestAnimationFrame(render);}
  function seek(fraction){
    const start=scrollY+route.getBoundingClientRect().top;
    window.scrollTo({top:start+(route.offsetHeight-view.clientHeight)*fraction,behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth'});
  }
  jump.addEventListener('click',()=>seek(Number(chapters[(previousStop+1)%chapters.length].dataset.at)));
  chapters.forEach(tab=>tab.addEventListener('click',()=>seek(Number(tab.dataset.at))));
  reducedMotion.addEventListener('change',schedule);
  window.addEventListener('scroll',schedule,{passive:true});new ResizeObserver(schedule).observe(view);schedule();
})();
