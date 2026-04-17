import { Renderer, Program, Mesh, Color, Triangle } from 'ogl';

const VERT = `#version 300 es
in vec2 position;
void main() {
  gl_Position = vec4(position, 0.0, 1.0);
}
`;

const FRAG = `#version 300 es
precision highp float;

uniform float uTime;
uniform float uAmplitude;
uniform vec3 uColorStops[3];
uniform vec2 uResolution;
uniform float uBlend;

out vec4 fragColor;

vec3 permute(vec3 x) {
  return mod(((x * 34.0) + 1.0) * x, 289.0);
}

float snoise(vec2 v){
  const vec4 C = vec4(
      0.211324865405187, 0.366025403784439,
      -0.577350269189626, 0.024390243902439
  );
  vec2 i  = floor(v + dot(v, C.yy));
  vec2 x0 = v - i + dot(i, C.xx);
  vec2 i1 = (x0.x > x0.y) ? vec2(1.0, 0.0) : vec2(0.0, 1.0);
  vec4 x12 = x0.xyxy + C.xxzz;
  x12.xy -= i1;
  i = mod(i, 289.0);

  vec3 p = permute(
      permute(i.y + vec3(0.0, i1.y, 1.0))
    + i.x + vec3(0.0, i1.x, 1.0)
  );

  vec3 m = max(
      0.5 - vec3(
          dot(x0, x0),
          dot(x12.xy, x12.xy),
          dot(x12.zw, x12.zw)
      ), 
      0.0
  );
  m = m * m;
  m = m * m;

  vec3 x = 2.0 * fract(p * C.www) - 1.0;
  vec3 h = abs(x) - 0.5;
  vec3 ox = floor(x + 0.5);
  vec3 a0 = x - ox;
  m *= 1.79284291400159 - 0.85373472095314 * (a0*a0 + h*h);

  vec3 g;
  g.x  = a0.x  * x0.x  + h.x  * x0.y;
  g.yz = a0.yz * x12.xz + h.yz * x12.yw;
  return 130.0 * dot(m, g);
}

struct ColorStop {
  vec3 color;
  float position;
};

#define COLOR_RAMP(colors, factor, finalColor) {              \
  int index = 0;                                            \
  for (int i = 0; i < 2; i++) {                               \
     ColorStop currentColor = colors[i];                    \
     bool isInBetween = currentColor.position <= factor;    \
     index = int(mix(float(index), float(i), float(isInBetween))); \
  }                                                         \
  ColorStop currentColor = colors[index];                   \
  ColorStop nextColor = colors[index + 1];                  \
  float range = nextColor.position - currentColor.position; \
  float lerpFactor = (factor - currentColor.position) / range; \
  finalColor = mix(currentColor.color, nextColor.color, lerpFactor); \
}

void main() {
  vec2 uv = gl_FragCoord.xy / uResolution;
  
  ColorStop colors[3];
  colors[0] = ColorStop(uColorStops[0], 0.0);
  colors[1] = ColorStop(uColorStops[1], 0.5);
  colors[2] = ColorStop(uColorStops[2], 1.0);
  
  vec3 rampColor;
  COLOR_RAMP(colors, uv.x, rampColor);
  
  float height = snoise(vec2(uv.x * 2.0 + uTime * 0.1, uTime * 0.25)) * 0.5 * uAmplitude;
  height = exp(height);
  height = (uv.y * 2.0 - height + 0.2);
  float intensity = 0.6 * height;
  
  float midPoint = 0.20;
  float auroraAlpha = smoothstep(midPoint - uBlend * 0.5, midPoint + uBlend * 0.5, intensity);
  
  vec3 auroraColor = intensity * rampColor;
  
  fragColor = vec4(auroraColor * auroraAlpha, auroraAlpha);
}
`;

export default class Aurora {
  constructor(container, options = {}) {
    this.container = container;
    this.options = {
      colorStops: options.colorStops || ['#5227FF', '#7cff67', '#5227FF'],
      amplitude: options.amplitude ?? 1.0,
      blend: options.blend ?? 0.5,
      speed: options.speed ?? 1.0,
      time: 0
    };
    
    this.init();
  }

  init() {
    if (!this.container) return;

    // Create canvas
    this.canvas = document.createElement('canvas');
    this.canvas.style.width = '100%';
    this.canvas.style.height = '100%';
    this.canvas.style.position = 'absolute';
    this.canvas.style.top = '0';
    this.canvas.style.left = '0';
    this.canvas.style.zIndex = '0';
    this.container.appendChild(this.canvas);

    // Initialize WebGL
    this.gl = this.canvas.getContext('webgl2', {
      alpha: true,
      premultipliedAlpha: true,
      antialias: true
    });

    if (!this.gl) {
      console.warn('WebGL 2 not supported, falling back to CSS aurora');
      this.fallback();
      return;
    }

    const gl = this.gl;
    gl.clearColor(0, 0, 0, 0);
    gl.enable(gl.BLEND);
    gl.blendFunc(gl.ONE, gl.ONE_MINUS_SRC_ALPHA);

    this.renderer = new Renderer({
      canvas: this.canvas,
      width: this.container.offsetWidth,
      height: this.container.offsetHeight
    });

    this.resize();
    window.addEventListener('resize', () => this.resize());

    // Create geometry
    const geometry = new Triangle(gl);
    if (geometry.attributes.uv) {
      delete geometry.attributes.uv;
    }

    // Create color stops
    const colorStopsArray = this.options.colorStops.map(hex => {
      const c = new Color(hex);
      return [c.r, c.g, c.b];
    });

    // Create program
    this.program = new Program(gl, {
      vertex: VERT,
      fragment: FRAG,
      uniforms: {
        uTime: { value: 0 },
        uAmplitude: { value: this.options.amplitude },
        uColorStops: { value: colorStopsArray },
        uResolution: { value: [this.container.offsetWidth, this.container.offsetHeight] },
        uBlend: { value: this.options.blend }
      }
    });

    this.mesh = new Mesh(gl, { geometry, program: this.program });
    
    this.animate();
  }

  fallback() {
    // CSS fallback for browsers without WebGL 2
    this.container.style.background = `
      linear-gradient(135deg, 
        ${this.options.colorStops[0]}40 0%, 
        ${this.options.colorStops[1]}30 50%, 
        ${this.options.colorStops[2]}40 100%)
    `;
  }

  resize() {
    if (!this.container || !this.renderer) return;
    const width = this.container.offsetWidth;
    const height = this.container.offsetHeight;
    this.renderer.setSize(width, height);
    if (this.program) {
      this.program.uniforms.uResolution.value = [width, height];
    }
    this.canvas.width = width;
    this.canvas.height = height;
  }

  animate() {
    if (!this.program) return;
    
    this.options.time += 0.01 * this.options.speed;
    this.program.uniforms.uTime.value = this.options.time;
    
    this.renderer.render({ scene: this.mesh });
    this.animationId = requestAnimationFrame(() => this.animate());
  }

  update(options) {
    if (!this.program) return;
    
    if (options.amplitude !== undefined) {
      this.program.uniforms.uAmplitude.value = options.amplitude;
    }
    if (options.blend !== undefined) {
      this.program.uniforms.uBlend.value = options.blend;
    }
    if (options.speed !== undefined) {
      this.options.speed = options.speed;
    }
    if (options.colorStops) {
      this.program.uniforms.uColorStops.value = options.colorStops.map(hex => {
        const c = new Color(hex);
        return [c.r, c.g, c.b];
      });
    }
  }

  destroy() {
    if (this.animationId) {
      cancelAnimationFrame(this.animationId);
    }
    window.removeEventListener('resize', () => this.resize());
    if (this.canvas && this.canvas.parentNode) {
      this.canvas.parentNode.removeChild(this.canvas);
    }
    if (this.gl) {
      const ext = this.gl.getExtension('WEBGL_lose_context');
      if (ext) ext.loseContext();
    }
  }
}
