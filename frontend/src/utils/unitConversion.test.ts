import { describe, it, expect } from 'vitest';
import {
  mlToTsp,
  tspToMl,
  mlToTbsp,
  tbspToMl,
  mlToFlOz,
  flOzToMl,
  kgToLbs,
  lbsToKg,
  convertVolume,
  convertWeight,
  getVolumeInSystem,
  getWeightInSystem,
  formatVolumeWithEquivalent,
  formatWeightWithEquivalent,
} from './unitConversion';

describe('Volume Conversions', () => {
  describe('mlToTsp', () => {
    it('converts 5mL to 1 tsp', () => {
      const result = mlToTsp(5);
      expect(result.value).toBe(1);
      expect(result.unit).toBe('tsp');
    });

    it('converts 15mL to 3 tsp', () => {
      const result = mlToTsp(15);
      expect(result.value).toBe(3);
    });

    it('converts 2.5mL to 0.5 tsp', () => {
      const result = mlToTsp(2.5);
      expect(result.value).toBe(0.5);
    });

    it('formats output correctly', () => {
      const result = mlToTsp(10);
      expect(result.formatted).toBe('2 tsp');
    });
  });

  describe('tspToMl', () => {
    it('converts 1 tsp to 5mL', () => {
      const result = tspToMl(1);
      expect(result.value).toBe(5);
      expect(result.unit).toBe('mL');
    });

    it('converts 2 tsp to 10mL', () => {
      const result = tspToMl(2);
      expect(result.value).toBe(10);
    });
  });

  describe('mlToTbsp', () => {
    it('converts 15mL to 1 tbsp', () => {
      const result = mlToTbsp(15);
      expect(result.value).toBe(1);
      expect(result.unit).toBe('tbsp');
    });

    it('converts 30mL to 2 tbsp', () => {
      const result = mlToTbsp(30);
      expect(result.value).toBe(2);
    });
  });

  describe('tbspToMl', () => {
    it('converts 1 tbsp to 15mL', () => {
      const result = tbspToMl(1);
      expect(result.value).toBe(15);
      expect(result.unit).toBe('mL');
    });

    it('converts 2 tbsp to 30mL', () => {
      const result = tbspToMl(2);
      expect(result.value).toBe(30);
    });
  });

  describe('mlToFlOz', () => {
    it('converts 29.5735mL to approximately 1 fl oz', () => {
      const result = mlToFlOz(29.5735);
      expect(result.value).toBe(1);
      expect(result.unit).toBe('fl oz');
    });

    it('converts 60mL to approximately 2 fl oz', () => {
      const result = mlToFlOz(60);
      expect(result.value).toBeCloseTo(2.03, 1);
    });

    it('converts 240mL to approximately 8 fl oz (1 cup)', () => {
      const result = mlToFlOz(240);
      expect(result.value).toBeCloseTo(8.1, 0);
    });
  });

  describe('flOzToMl', () => {
    it('converts 1 fl oz to approximately 29.57mL', () => {
      const result = flOzToMl(1);
      expect(result.value).toBeCloseTo(29.57, 1);
      expect(result.unit).toBe('mL');
    });

    it('converts 8 fl oz to approximately 237mL', () => {
      const result = flOzToMl(8);
      expect(result.value).toBeCloseTo(237, 0);
    });
  });
});

describe('Weight Conversions', () => {
  describe('kgToLbs', () => {
    it('converts 1 kg to approximately 2.2 lbs', () => {
      const result = kgToLbs(1);
      expect(result.value).toBeCloseTo(2.2, 1);
      expect(result.unit).toBe('lbs');
    });

    it('converts 70 kg to approximately 154 lbs', () => {
      const result = kgToLbs(70);
      expect(result.value).toBeCloseTo(154.3, 0);
    });

    it('formats output correctly', () => {
      const result = kgToLbs(50);
      expect(result.formatted).toBe('110.2 lbs');
    });
  });

  describe('lbsToKg', () => {
    it('converts 2.2 lbs to approximately 1 kg', () => {
      const result = lbsToKg(2.2);
      expect(result.value).toBeCloseTo(1, 1);
      expect(result.unit).toBe('kg');
    });

    it('converts 150 lbs to approximately 68 kg', () => {
      const result = lbsToKg(150);
      expect(result.value).toBeCloseTo(68, 0);
    });
  });
});

describe('Generic Conversion Functions', () => {
  describe('convertVolume', () => {
    it('converts between different volume units', () => {
      expect(convertVolume(15, 'mL', 'tbsp').value).toBe(1);
      expect(convertVolume(1, 'tbsp', 'mL').value).toBe(15);
      expect(convertVolume(3, 'tsp', 'tbsp').value).toBe(1);
    });

    it('handles same unit conversion', () => {
      expect(convertVolume(100, 'mL', 'mL').value).toBe(100);
    });

    it('converts from fl oz to tsp', () => {
      const result = convertVolume(1, 'fl oz', 'tsp');
      expect(result.value).toBeCloseTo(5.9, 0);
    });
  });

  describe('convertWeight', () => {
    it('converts between kg and lbs', () => {
      expect(convertWeight(1, 'kg', 'lbs').value).toBeCloseTo(2.2, 1);
      expect(convertWeight(2.2, 'lbs', 'kg').value).toBeCloseTo(1, 1);
    });

    it('handles same unit conversion', () => {
      expect(convertWeight(70, 'kg', 'kg').value).toBe(70);
    });
  });
});

describe('Unit System Functions', () => {
  describe('getVolumeInSystem', () => {
    it('returns mL for metric system', () => {
      const result = getVolumeInSystem(100, 'metric');
      expect(result.value).toBe(100);
      expect(result.unit).toBe('mL');
    });

    it('returns tsp for small imperial volumes', () => {
      const result = getVolumeInSystem(10, 'imperial');
      expect(result.value).toBe(2);
      expect(result.unit).toBe('tsp');
    });

    it('returns tbsp for medium imperial volumes', () => {
      const result = getVolumeInSystem(60, 'imperial');
      expect(result.value).toBe(4);
      expect(result.unit).toBe('tbsp');
    });

    it('returns fl oz for large imperial volumes', () => {
      const result = getVolumeInSystem(240, 'imperial');
      expect(result.unit).toBe('fl oz');
    });
  });

  describe('getWeightInSystem', () => {
    it('returns kg for metric system', () => {
      const result = getWeightInSystem(70, 'metric');
      expect(result.value).toBe(70);
      expect(result.unit).toBe('kg');
    });

    it('returns lbs for imperial system', () => {
      const result = getWeightInSystem(70, 'imperial');
      expect(result.value).toBeCloseTo(154.3, 0);
      expect(result.unit).toBe('lbs');
    });
  });
});

describe('Formatting Functions', () => {
  describe('formatVolumeWithEquivalent', () => {
    it('formats 5mL as "5 mL (1 tsp)"', () => {
      const result = formatVolumeWithEquivalent(5);
      expect(result).toBe('5 mL (1 tsp)');
    });

    it('formats 15mL with tsp equivalent (small amount)', () => {
      const result = formatVolumeWithEquivalent(15);
      expect(result).toBe('15 mL (3 tsp)');
    });

    it('formats 30mL with tsp equivalent (small amount)', () => {
      const result = formatVolumeWithEquivalent(30);
      expect(result).toBe('30 mL (6 tsp)');
    });

    it('formats 60mL with tbsp equivalent (medium amount)', () => {
      const result = formatVolumeWithEquivalent(60);
      expect(result).toBe('60 mL (4 tbsp)');
    });

    it('formats 240mL with fl oz equivalent (large amount)', () => {
      const result = formatVolumeWithEquivalent(240);
      expect(result).toMatch(/240 mL \([\d.]+ fl oz\)/);
    });
  });

  describe('formatWeightWithEquivalent', () => {
    it('formats 70 kg with lbs equivalent', () => {
      const result = formatWeightWithEquivalent(70);
      expect(result).toBe('70 kg (154.3 lbs)');
    });

    it('formats 1 kg with lbs equivalent', () => {
      const result = formatWeightWithEquivalent(1);
      expect(result).toBe('1 kg (2.2 lbs)');
    });
  });
});

describe('Edge Cases', () => {
  it('handles zero values', () => {
    expect(mlToTsp(0).value).toBe(0);
    expect(kgToLbs(0).value).toBe(0);
  });

  it('handles very small values', () => {
    const result = mlToTsp(0.5);
    expect(result.value).toBe(0.1);
  });

  it('rounds appropriately for display', () => {
    // Large values should round to 1 decimal place
    const result = mlToFlOz(1000);
    expect(result.value).toBe(33.8);
  });
});
