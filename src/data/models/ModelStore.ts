import { STLModel } from '../../core/types/STLModel';

/**
 * 模型状态接口
 */
export interface ModelState {
  /** 是否正在加载 */
  isLoading: boolean;
  /** 当前加载的模型 */
  currentModel: STLModel | null;
  /** 错误信息 */
  error: string | null;
  /** 加载进度 (0-100) */
  progress: number;
}

/**
 * 状态变化监听器类型
 */
export type StateListener = (state: ModelState) => void;

/**
 * 初始状态常量
 */
const INITIAL_STATE: ModelState = {
  isLoading: false,
  currentModel: null,
  error: null,
  progress: 0
};

/**
 * 模型状态管理存储
 * 职责：管理模型加载状态，提供状态订阅机制
 */
export class ModelStore {
  private state: ModelState;
  private listeners: StateListener[];
  private history: ModelState[];

  constructor() {
    this.state = { ...INITIAL_STATE };
    this.listeners = [];
    this.history = [this.getStateSnapshot()];
  }

  /**
   * 获取当前状态
   */
  getState(): ModelState {
    return this.getStateSnapshot();
  }

  /**
   * 开始加载状态
   */
  startLoading(): void {
    this.updateState({
      isLoading: true,
      currentModel: null,
      error: null,
      progress: 0
    });
  }

  /**
   * 设置加载成功状态
   * @param model 加载成功的模型
   */
  setSuccess(model: STLModel): void {
    this.updateState({
      isLoading: false,
      currentModel: model,
      error: null,
      progress: 100
    });
  }

  /**
   * 设置加载失败状态
   * @param error 错误信息
   */
  setError(error: string): void {
    this.updateState({
      isLoading: false,
      currentModel: null,
      error,
      progress: 0
    });
  }

  /**
   * 更新加载进度
   * @param progress 进度值 (0-100)
   */
  updateProgress(progress: number): void {
    // 验证进度值范围
    const validatedProgress = Math.max(0, Math.min(100, progress));
    this.updateState({
      ...this.state,
      progress: validatedProgress
    });
  }

  /**
   * 重置状态
   */
  reset(): void {
    this.updateState({ ...INITIAL_STATE });
  }

  /**
   * 订阅状态变化
   * @param listener 状态变化监听器
   * @returns 取消订阅函数
   */
  subscribe(listener: StateListener): () => void {
    this.listeners.push(listener);
    
    // 立即调用一次以获取当前状态
    listener(this.getState());

    return () => {
      const index = this.listeners.indexOf(listener);
      if (index > -1) {
        this.listeners.splice(index, 1);
      }
    };
  }

  /**
   * 获取状态变化历史
   */
  getHistory(): ModelState[] {
    return [...this.history];
  }

  /**
   * 序列化状态
   */
  serialize(): string {
    return JSON.stringify(this.state);
  }

  /**
   * 反序列化状态
   * @param serialized 序列化的状态字符串
   */
  deserialize(serialized: string): void {
    try {
      const parsedState = JSON.parse(serialized);
      this.updateState(parsedState);
    } catch (error) {
      console.error('状态反序列化失败:', error);
    }
  }

  /**
   * 更新状态并通知监听器
   * @param newState 新的状态
   */
  private updateState(newState: ModelState): void {
    this.state = newState;
    this.history.push(this.getStateSnapshot());
    
    // 通知所有监听器
    this.listeners.forEach(listener => {
      try {
        listener(this.getState());
      } catch (error) {
        console.error('状态监听器执行失败:', error);
      }
    });
  }

  /**
   * 获取状态快照（深拷贝）
   */
  private getStateSnapshot(): ModelState {
    return {
      isLoading: this.state.isLoading,
      currentModel: this.state.currentModel ? {
        ...this.state.currentModel,
        vertices: [...this.state.currentModel.vertices],
        normals: [...this.state.currentModel.normals],
        faces: [...this.state.currentModel.faces]
      } : null,
      error: this.state.error,
      progress: this.state.progress
    };
  }
}
