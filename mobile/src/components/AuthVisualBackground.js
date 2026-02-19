import React, { useEffect, useMemo, useRef, useState } from 'react';
import { Animated, Easing, StyleSheet, View, useWindowDimensions } from 'react-native';
import Svg, { Circle, Line } from 'react-native-svg';

const NODE_COUNT = 30;
const MAX_DISTANCE = 150;
const GRID_SIZE = 90;

function createNodes(width, height, count = NODE_COUNT) {
  return Array.from({ length: count }).map(() => ({
    x: Math.random() * width,
    y: Math.random() * height,
    vx: (Math.random() - 0.5) * 0.55,
    vy: (Math.random() - 0.5) * 0.55,
  }));
}

export default function AuthVisualBackground({ children }) {
  const { width, height } = useWindowDimensions();
  const nodesRef = useRef(createNodes(width, height));
  const frameRef = useRef(null);
  const [, setTick] = useState(0);

  const blobA = useRef(new Animated.Value(0)).current;
  const blobB = useRef(new Animated.Value(0)).current;
  const blobC = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    nodesRef.current = createNodes(width, height);
  }, [width, height]);

  useEffect(() => {
    const animate = () => {
      const nodes = nodesRef.current;
      for (let i = 0; i < nodes.length; i += 1) {
        const node = nodes[i];
        node.x += node.vx;
        node.y += node.vy;

        if (node.x < 0 || node.x > width) node.vx *= -1;
        if (node.y < 0 || node.y > height) node.vy *= -1;
      }
      setTick((value) => (value + 1) % 10000);
      frameRef.current = requestAnimationFrame(animate);
    };

    frameRef.current = requestAnimationFrame(animate);
    return () => {
      if (frameRef.current) cancelAnimationFrame(frameRef.current);
    };
  }, [width, height]);

  useEffect(() => {
    const makeFloat = (animatedValue, duration, delay = 0) =>
      Animated.loop(
        Animated.sequence([
          Animated.timing(animatedValue, {
            toValue: 1,
            duration,
            delay,
            easing: Easing.inOut(Easing.quad),
            useNativeDriver: true,
          }),
          Animated.timing(animatedValue, {
            toValue: 0,
            duration,
            easing: Easing.inOut(Easing.quad),
            useNativeDriver: true,
          }),
        ])
      );

    const a = makeFloat(blobA, 4000, 0);
    const b = makeFloat(blobB, 4500, 600);
    const c = makeFloat(blobC, 5000, 1000);

    a.start();
    b.start();
    c.start();

    return () => {
      a.stop();
      b.stop();
      c.stop();
    };
  }, [blobA, blobB, blobC]);

  const gridLines = useMemo(() => {
    const vertical = [];
    const horizontal = [];

    for (let x = 0; x <= width; x += GRID_SIZE) {
      vertical.push(
        <Line key={`vx-${x}`} x1={x} y1={0} x2={x} y2={height} stroke="rgba(255,0,128,0.07)" strokeWidth={1} />
      );
    }
    for (let y = 0; y <= height; y += GRID_SIZE) {
      horizontal.push(
        <Line key={`hy-${y}`} x1={0} y1={y} x2={width} y2={y} stroke="rgba(255,0,128,0.07)" strokeWidth={1} />
      );
    }

    return [...vertical, ...horizontal];
  }, [width, height]);

  const lines = [];
  const nodes = nodesRef.current;
  for (let i = 0; i < nodes.length; i += 1) {
    for (let j = i + 1; j < nodes.length; j += 1) {
      const dx = nodes[i].x - nodes[j].x;
      const dy = nodes[i].y - nodes[j].y;
      const distance = Math.sqrt(dx * dx + dy * dy);
      if (distance < MAX_DISTANCE) {
        const alpha = (1 - distance / MAX_DISTANCE) * 0.35;
        lines.push(
          <Line
            key={`l-${i}-${j}`}
            x1={nodes[i].x}
            y1={nodes[i].y}
            x2={nodes[j].x}
            y2={nodes[j].y}
            stroke={`rgba(180, 32, 176, ${alpha})`}
            strokeWidth={1.2}
          />
        );
      }
    }
  }

  return (
    <View style={styles.container}>
      <View style={StyleSheet.absoluteFill}>
        <Svg width={width} height={height} pointerEvents="none">
          {gridLines}
        </Svg>
      </View>

      <Animated.View
        style={[
          styles.blob,
          styles.blobA,
          {
            transform: [
              {
                translateY: blobA.interpolate({
                  inputRange: [0, 1],
                  outputRange: [0, -28],
                }),
              },
              {
                scale: blobA.interpolate({
                  inputRange: [0, 1],
                  outputRange: [1, 1.15],
                }),
              },
            ],
          },
        ]}
      />
      <Animated.View
        style={[
          styles.blob,
          styles.blobB,
          {
            transform: [
              {
                translateY: blobB.interpolate({
                  inputRange: [0, 1],
                  outputRange: [0, -24],
                }),
              },
              {
                scale: blobB.interpolate({
                  inputRange: [0, 1],
                  outputRange: [1, 1.1],
                }),
              },
            ],
          },
        ]}
      />
      <Animated.View
        style={[
          styles.blob,
          styles.blobC,
          {
            transform: [
              {
                translateY: blobC.interpolate({
                  inputRange: [0, 1],
                  outputRange: [0, -32],
                }),
              },
              {
                scale: blobC.interpolate({
                  inputRange: [0, 1],
                  outputRange: [1, 1.18],
                }),
              },
            ],
          },
        ]}
      />

      <View style={StyleSheet.absoluteFill}>
        <Svg width={width} height={height} pointerEvents="none">
          {lines}
          {nodes.map((node, index) => (
          <React.Fragment key={`n-${index}`}>
              <Circle cx={node.x} cy={node.y} r={8} fill="rgba(255, 0, 128, 0.18)" />
              <Circle cx={node.x} cy={node.y} r={2.3} fill="rgba(255, 0, 128, 0.9)" />
            </React.Fragment>
          ))}
        </Svg>
      </View>

      {children}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#FFFFFF',
    overflow: 'hidden',
  },
  blob: {
    position: 'absolute',
    borderRadius: 999,
    opacity: 0.3,
  },
  blobA: {
    width: 280,
    height: 280,
    left: '8%',
    top: '16%',
    backgroundColor: 'rgba(255, 0, 128, 0.18)',
  },
  blobB: {
    width: 320,
    height: 320,
    right: '5%',
    bottom: '12%',
    backgroundColor: 'rgba(121, 40, 202, 0.16)',
  },
  blobC: {
    width: 220,
    height: 220,
    left: '42%',
    top: '44%',
    backgroundColor: 'rgba(137, 8, 204, 0.14)',
  },
});
