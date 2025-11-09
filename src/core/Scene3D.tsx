import React, { useRef, useEffect, useCallback } from 'react';
import * as THREE from 'three';

/**
 * STL模型数据接口
 * @interface STLModel
 * @property {number[]} vertices - 顶点数据数组，每3个元素表示一个顶点的x,y,z坐标
 * @property {number[]} normals - 法线数据数组，每3个元素表示一个法线的x,y,z分量
 * @property {number[]} faces - 面索引数组，每3个元素表示一个三角形的顶点索引
 */
interface STLModel {
  vertices: number[];
  normals: number[];
  faces: number[];
}

/**
 * 3D场景配置接口
 * @interface SceneConfig
 * @property {number} [backgroundColor=0xf0f0f0] - 场景背景颜色，十六进制格式
 * @property {number} [cubeColor=0x00ff00] - 默认立方体颜色，十六进制格式
 * @property {number} [cubeSize=1] - 默认立方体尺寸
 * @property {number} [cameraDistance=12.5] - 相机距离，默认对应缩放值50
 * @property {number} [animationSpeed=0.01] - 动画速度，已取消自动旋转
 * @property {STLModel | null} [model=null] - STL模型数据
 * @property {boolean} [showDefaultCube=true] - 是否显示默认立方体
 */
interface SceneConfig {
  backgroundColor?: number;
  cubeColor?: number;
  cubeSize?: number;
  cameraDistance?: number;
  animationSpeed?: number;
  /** STL模型数据 */
  model?: STLModel | null;
  /** 是否显示默认立方体 */
  showDefaultCube?: boolean;
}

/**
 * 3D场景组件
 * 基于Three.js的3D渲染场景，支持STL模型加载和缩放功能
 * 
 * @component
 * @param {SceneConfig} props - 场景配置参数
 * @param {number} [props.backgroundColor=0xf0f0f0] - 场景背景颜色
 * @param {number} [props.cubeColor=0x00ff00] - 默认立方体颜色
 * @param {number} [props.cubeSize=1] - 默认立方体尺寸
 * @param {number} [props.cameraDistance=12.5] - 相机距离，默认对应缩放值50
 * @param {number} [props.animationSpeed=0.01] - 动画速度，已取消自动旋转
 * @param {STLModel | null} [props.model=null] - STL模型数据
 * @param {boolean} [props.showDefaultCube=true] - 是否显示默认立方体
 * 
 * @example
 * ```tsx
 * // 基本用法
 * <Scene3D />
 * 
 * // 自定义配置
 * <Scene3D 
 *   backgroundColor={0x000000}
 *   cameraDistance={15}
 *   model={stlModelData}
 *   showDefaultCube={false}
 * />
 * ```
 * 
 * 重构改进：
 * - 添加配置参数，提高组件可配置性
 * - 分离场景初始化逻辑，提高代码可读性
 * - 使用useCallback优化动画函数
 * - 添加窗口大小变化响应
 * - 改进错误处理和资源清理
 * - 提取常量定义，提高代码可维护性
 * - 优化光照配置，提高渲染质量
 * - 自动按比例显示模型，确保完整显示
 * - 取消自动旋转，降低硬件要求
 */
const Scene3D: React.FC<SceneConfig> = ({
  backgroundColor = 0xf0f0f0,
  cubeColor = 0x00ff00,
  cubeSize = 1,
  cameraDistance = 12.5, // 默认对应缩放值50
  animationSpeed = 0.01,
  model = null,
  showDefaultCube = true
}) => {
  const mountRef = useRef<HTMLDivElement>(null);
  const sceneRef = useRef<THREE.Scene | null>(null);
  const cameraRef = useRef<THREE.PerspectiveCamera | null>(null);
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
  const cubeRef = useRef<THREE.Mesh | null>(null);
  const modelRef = useRef<THREE.Mesh | null>(null);
  const animationIdRef = useRef<number | null>(null);

  /**
   * 初始化3D场景
   */
  const initializeScene = useCallback(() => {
    if (!mountRef.current) return null;

    console.log('Scene3D: 初始化场景，相机距离:', cameraDistance);

    // 场景初始化
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, mountRef.current.clientWidth / mountRef.current.clientHeight, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({ antialias: true });

    // 渲染器配置
    renderer.setSize(mountRef.current.clientWidth, mountRef.current.clientHeight);
    renderer.setClearColor(backgroundColor);
    mountRef.current.appendChild(renderer.domElement);

    // 基础几何体（可选）
    if (showDefaultCube) {
      const geometry = new THREE.BoxGeometry(cubeSize, cubeSize, cubeSize);
      const material = new THREE.MeshBasicMaterial({ color: cubeColor });
      const cube = new THREE.Mesh(geometry, material);
      scene.add(cube);
      cubeRef.current = cube;
    }

    // 相机位置
    camera.position.z = cameraDistance;
    camera.updateProjectionMatrix(); // 确保相机矩阵更新

    // 保存引用
    sceneRef.current = scene;
    cameraRef.current = camera;
    rendererRef.current = renderer;

    // 初始渲染
    renderer.render(scene, camera);

    return { scene, camera, renderer };
  }, [backgroundColor, cubeColor, cubeSize, showDefaultCube]); // 移除cameraDistance依赖

  /**
   * 计算适合模型大小的相机距离
   */
  const calculateOptimalCameraDistance = useCallback((geometry: THREE.BufferGeometry): number => {
    if (!geometry.boundingBox) return 12.5; // 默认距离

    const boxSize = new THREE.Vector3();
    geometry.boundingBox.getSize(boxSize);
    
    // 计算模型的最大尺寸
    const maxDimension = Math.max(boxSize.x, boxSize.y, boxSize.z);
    console.log('Scene3D: 模型尺寸:', boxSize, '最大尺寸:', maxDimension);
    
    // 根据模型大小计算合适的相机距离
    // 使用模型尺寸的2倍作为基础距离，确保模型完整显示
    const baseDistance = maxDimension * 2;
    
    // 限制最小和最大距离
    const minDistance = 5;
    const maxDistance = 100;
    
    const optimalDistance = Math.max(minDistance, Math.min(maxDistance, baseDistance));
    console.log('Scene3D: 计算出的最佳相机距离:', optimalDistance);
    
    return optimalDistance;
  }, []);

  /**
   * 加载STL模型
   */
  const loadSTLModel = useCallback((modelData: STLModel) => {
    if (!sceneRef.current) return;

    console.log('Scene3D: 加载STL模型，顶点数:', modelData.vertices.length / 3);

    // 清理现有模型
    if (modelRef.current) {
      sceneRef.current.remove(modelRef.current);
      modelRef.current = null;
    }

    // 创建几何体
    const geometry = new THREE.BufferGeometry();
    
    // 设置顶点
    const vertices = new Float32Array(modelData.vertices);
    geometry.setAttribute('position', new THREE.BufferAttribute(vertices, 3));
    
    // 设置法线
    if (modelData.normals && modelData.normals.length > 0) {
      const normals = new Float32Array(modelData.normals);
      geometry.setAttribute('normal', new THREE.BufferAttribute(normals, 3));
    }
    
    // 设置面
    if (modelData.faces && modelData.faces.length > 0) {
      const indices = new Uint32Array(modelData.faces);
      geometry.setIndex(new THREE.BufferAttribute(indices, 1));
    }

    // 计算边界框和中心点
    geometry.computeBoundingBox();
    geometry.computeBoundingSphere();

    console.log('Scene3D: 模型边界框:', geometry.boundingBox);

    // 计算适合模型大小的相机距离
    const optimalDistance = calculateOptimalCameraDistance(geometry);

    // 创建材质和网格
    const material = new THREE.MeshPhongMaterial({ 
      color: 0x2196f3,
      specular: 0x111111,
      shininess: 30,
      transparent: true,
      opacity: 0.8
    });
    
    const mesh = new THREE.Mesh(geometry, material);
    
    // 调整模型位置到场景中心
    if (geometry.boundingBox) {
      const center = geometry.boundingBox.getCenter(new THREE.Vector3());
      console.log('Scene3D: 模型中心位置:', center);
      // 将模型移动到场景中心，确保在相机视野内
      mesh.position.set(-center.x, -center.y, -center.z);
    }

    sceneRef.current.add(mesh);
    modelRef.current = mesh;

    // 添加环境光
    const ambientLight = new THREE.AmbientLight(0x404040, 0.6);
    sceneRef.current.add(ambientLight);

    // 添加方向光
    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(1, 1, 1);
    sceneRef.current.add(directionalLight);

    // 更新相机距离以完整显示模型
    if (cameraRef.current) {
      cameraRef.current.position.z = optimalDistance;
      cameraRef.current.updateProjectionMatrix();
      console.log('Scene3D: 更新相机距离以完整显示模型:', optimalDistance);
    }

    // 强制重绘
    if (sceneRef.current && cameraRef.current && rendererRef.current) {
      rendererRef.current.render(sceneRef.current, cameraRef.current);
    }

  }, [calculateOptimalCameraDistance]);

  /**
   * 动画循环
   */
  const animate = useCallback(() => {
    if (!sceneRef.current || !cameraRef.current || !rendererRef.current) return;

    // 取消自动旋转以降低硬件要求
    // 如果需要旋转，可以通过用户交互控制
    
    rendererRef.current.render(sceneRef.current, cameraRef.current);
    animationIdRef.current = requestAnimationFrame(animate);
  }, []);

  /**
   * 处理窗口大小变化
   */
  const handleResize = useCallback(() => {
    if (!cameraRef.current || !rendererRef.current || !mountRef.current) return;

    cameraRef.current.aspect = mountRef.current.clientWidth / mountRef.current.clientHeight;
    cameraRef.current.updateProjectionMatrix();
    rendererRef.current.setSize(mountRef.current.clientWidth, mountRef.current.clientHeight);
  }, []);

  /**
   * 清理资源
   */
  const cleanup = useCallback(() => {
    if (animationIdRef.current) {
      cancelAnimationFrame(animationIdRef.current);
    }

    if (rendererRef.current && mountRef.current) {
      mountRef.current.removeChild(rendererRef.current.domElement);
      rendererRef.current.dispose();
    }

    // 清理引用
    sceneRef.current = null;
    cameraRef.current = null;
    rendererRef.current = null;
    cubeRef.current = null;
    animationIdRef.current = null;
  }, []);

  useEffect(() => {
    const sceneObjects = initializeScene();
    if (!sceneObjects) return;

    // 启动动画
    animate();

    // 添加窗口大小变化监听
    window.addEventListener('resize', handleResize);

    // 清理函数
    return () => {
      cleanup();
      window.removeEventListener('resize', handleResize);
    };
  }, [initializeScene, animate, handleResize, cleanup]);

  /**
   * 响应相机距离变化
   */
  useEffect(() => {
    if (cameraRef.current) {
      console.log('Scene3D: 更新相机距离:', cameraDistance);
      cameraRef.current.position.z = cameraDistance;
      cameraRef.current.updateProjectionMatrix(); // 确保相机矩阵更新
      // 强制重绘以显示缩放效果
      if (sceneRef.current && cameraRef.current && rendererRef.current) {
        rendererRef.current.render(sceneRef.current, cameraRef.current);
      }
    }
  }, [cameraDistance]);

  /**
   * 响应模型变化
   */
  useEffect(() => {
    if (model) {
      loadSTLModel(model);
    } else if (modelRef.current && sceneRef.current) {
      // 清理模型
      sceneRef.current.remove(modelRef.current);
      modelRef.current = null;
    }
  }, [model, loadSTLModel]);

  return (
    <div 
      ref={mountRef} 
      style={{ width: '100%', height: '100%' }}
      data-testid="3d-scene"
      role="img"
      aria-label="3D场景展示"
    />
  );
};

export default Scene3D;
