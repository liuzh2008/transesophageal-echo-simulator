import React, { useRef, useEffect, useCallback } from 'react';
import * as THREE from 'three';

/**
 * 3D场景配置接口
 */
interface SceneConfig {
  backgroundColor?: number;
  cubeColor?: number;
  cubeSize?: number;
  cameraDistance?: number;
  animationSpeed?: number;
}

/**
 * 3D场景组件
 * 基于Three.js的3D渲染场景
 * 
 * 重构改进：
 * - 添加配置参数，提高组件可配置性
 * - 分离场景初始化逻辑，提高代码可读性
 * - 使用useCallback优化动画函数
 * - 添加窗口大小变化响应
 * - 改进错误处理和资源清理
 */
const Scene3D: React.FC<SceneConfig> = ({
  backgroundColor = 0xf0f0f0,
  cubeColor = 0x00ff00,
  cubeSize = 1,
  cameraDistance = 5,
  animationSpeed = 0.01
}) => {
  const mountRef = useRef<HTMLDivElement>(null);
  const sceneRef = useRef<THREE.Scene | null>(null);
  const cameraRef = useRef<THREE.PerspectiveCamera | null>(null);
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
  const cubeRef = useRef<THREE.Mesh | null>(null);
  const animationIdRef = useRef<number | null>(null);

  /**
   * 初始化3D场景
   */
  const initializeScene = useCallback(() => {
    if (!mountRef.current) return null;

    // 场景初始化
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, mountRef.current.clientWidth / mountRef.current.clientHeight, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({ antialias: true });

    // 渲染器配置
    renderer.setSize(mountRef.current.clientWidth, mountRef.current.clientHeight);
    renderer.setClearColor(backgroundColor);
    mountRef.current.appendChild(renderer.domElement);

    // 基础几何体
    const geometry = new THREE.BoxGeometry(cubeSize, cubeSize, cubeSize);
    const material = new THREE.MeshBasicMaterial({ color: cubeColor });
    const cube = new THREE.Mesh(geometry, material);
    scene.add(cube);

    // 相机位置
    camera.position.z = cameraDistance;

    // 保存引用
    sceneRef.current = scene;
    cameraRef.current = camera;
    rendererRef.current = renderer;
    cubeRef.current = cube;

    return { scene, camera, renderer, cube };
  }, [backgroundColor, cubeColor, cubeSize, cameraDistance]);

  /**
   * 动画循环
   */
  const animate = useCallback(() => {
    if (!cubeRef.current || !sceneRef.current || !cameraRef.current || !rendererRef.current) return;

    cubeRef.current.rotation.x += animationSpeed;
    cubeRef.current.rotation.y += animationSpeed;
    
    rendererRef.current.render(sceneRef.current, cameraRef.current);
    animationIdRef.current = requestAnimationFrame(animate);
  }, [animationSpeed]);

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
      cameraRef.current.position.z = cameraDistance;
    }
  }, [cameraDistance]);

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
