import React, { useEffect, useRef } from 'react';
import { Image, StyleSheet, Animated, Easing } from 'react-native';
import AuthVisualBackground from '../components/AuthVisualBackground';

const logo = require('../../assets/brand/logo-nodo.png');

export default function SplashScreen() {
    const fadeAnim = useRef(new Animated.Value(0)).current;
    const scaleAnim = useRef(new Animated.Value(0.96)).current;
    const exitTranslateX = useRef(new Animated.Value(0)).current;

    useEffect(() => {
        Animated.parallel([
            Animated.timing(fadeAnim, {
                toValue: 1,
                duration: 500,
                useNativeDriver: true,
            }),
            Animated.timing(scaleAnim, {
                toValue: 1,
                duration: 500,
                easing: Easing.out(Easing.cubic),
                useNativeDriver: true,
            }),
        ]).start();

        const exitDelay = setTimeout(() => {
            Animated.parallel([
                Animated.timing(exitTranslateX, {
                    toValue: 42,
                    duration: 520,
                    easing: Easing.in(Easing.cubic),
                    useNativeDriver: true,
                }),
                Animated.timing(scaleAnim, {
                    toValue: 1.06,
                    duration: 520,
                    easing: Easing.in(Easing.cubic),
                    useNativeDriver: true,
                }),
                Animated.timing(fadeAnim, {
                    toValue: 0,
                    duration: 520,
                    easing: Easing.in(Easing.cubic),
                    useNativeDriver: true,
                }),
            ]).start();
        }, 2400);

        return () => clearTimeout(exitDelay);
    }, []);

    return (
        <AuthVisualBackground>
            <Animated.View
                style={{
                    opacity: fadeAnim,
                    transform: [{ scale: scaleAnim }, { translateX: exitTranslateX }],
                    alignItems: 'center',
                    justifyContent: 'center',
                    flex: 1,
                }}
            >
                <Image source={logo} style={styles.logo} resizeMode="contain" />
            </Animated.View>
        </AuthVisualBackground>
    );
}

const styles = StyleSheet.create({
    logo: {
        width: 300,
        height: 300,
    },
});
