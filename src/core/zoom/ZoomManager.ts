/**
 * 缩放管理器
 * 负责管理3D场景的缩放状态和业务逻辑
 * 
 * 关注点分离：状态管理和业务逻辑
 */

/**
 * 缩放状态接口
 * @interface ZoomState
 * @property {number} value - 当前缩放值，范围0-100
 * @property {number} min - 最小缩放值，默认0
 * @property {number} max - 最大缩放值，默认100
 * @property {number} step - 缩放步长，默认1
 */
export interface ZoomState {
  value: number;
  min: number;
  max: number;
  step: number;
}

/**
 * 缩放管理器接口
 * @interface ZoomManager
 * @method getState - 获取当前缩放状态
 * @method setZoom - 设置缩放值
 * @method reset - 重置缩放状态
 * @method isValidZoom - 验证缩放值是否有效
 */
export interface ZoomManager {
  getState(): ZoomState;
  setZoom(value: number): void;
  reset(): void;
  isValidZoom(value: number): boolean;
}

/**
 * 创建缩放管理器实例
 * @function createZoomManager
 * @param {Partial<ZoomState>} [initialState] - 初始状态配置
 * @returns {ZoomManager} 缩放管理器实例
 * @example
 * ```typescript
 * const zoomManager = createZoomManager({ value: 50, min: 0, max: 100 });
 * ```
 */
export const createZoomManager = (initialState?: Partial<ZoomState>): ZoomManager => {
  const state: ZoomState = {
    value: initialState?.value ?? 50,
    min: initialState?.min ?? 0,
    max: initialState?.max ?? 100,
    step: initialState?.step ?? 1,
  };

  return {
    getState(): ZoomState {
      return { ...state };
    },

    setZoom(value: number): void {
      if (this.isValidZoom(value)) {
        state.value = value;
      } else {
        console.warn(`缩放值 ${value} 超出有效范围 [${state.min}, ${state.max}]`);
      }
    },

    reset(): void {
      state.value = 50; // 默认中间值
    },

    isValidZoom(value: number): boolean {
      return value >= state.min && value <= state.max;
    }
  };
};

/**
 * 缩放值转换工具
 * 将UI缩放值(0-100)转换为3D场景相机距离
 * @function zoomValueToCameraDistance
 * @param {number} zoomValue - UI缩放值，范围0-100
 * @returns {number} 3D场景相机距离，范围2-10
 * @example
 * ```typescript
 * const distance = zoomValueToCameraDistance(50); // 返回6
 * ```
 */
export const zoomValueToCameraDistance = (zoomValue: number): number => {
  // 缩放值0对应最远距离(10)，缩放值100对应最近距离(2)
  const minDistance = 2;
  const maxDistance = 10;
  return maxDistance - (zoomValue / 100) * (maxDistance - minDistance);
};

/**
 * 缩放值转换工具
 * 将3D场景相机距离转换为UI缩放值(0-100)
 * @function cameraDistanceToZoomValue
 * @param {number} distance - 3D场景相机距离，范围2-10
 * @returns {number} UI缩放值，范围0-100
 * @example
 * ```typescript
 * const zoomValue = cameraDistanceToZoomValue(6); // 返回50
 * ```
 */
export const cameraDistanceToZoomValue = (distance: number): number => {
  const minDistance = 2;
  const maxDistance = 10;
  return ((maxDistance - distance) / (maxDistance - minDistance)) * 100;
};
