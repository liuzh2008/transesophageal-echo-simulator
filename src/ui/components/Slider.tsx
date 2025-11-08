import React from 'react';

/**
 * 滑块组件
 * 提供数值范围选择功能
 */
interface SliderProps {
  value: number;
  min?: number;
  max?: number;
  step?: number;
  onChange?: (value: number) => void;
}

const Slider: React.FC<SliderProps> = ({ 
  value, 
  min = 0, 
  max = 100, 
  step = 1,
  onChange 
}) => {
  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = parseFloat(event.target.value);
    onChange?.(newValue);
  };

  return (
    <div data-testid="slider" className="slider">
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={handleChange}
        className="slider__input"
      />
      <span className="slider__value">{value}</span>
    </div>
  );
};

export default Slider;
