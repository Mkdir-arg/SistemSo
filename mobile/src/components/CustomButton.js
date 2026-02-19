import React, { useRef } from 'react';
import { Pressable, Text, StyleSheet, View, Platform, Animated, ActivityIndicator } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { useTheme } from '../context/ThemeContext';
import { Ionicons } from '@expo/vector-icons';

const SIZES = {
    XS: { h: 32, px: 12, fontSize: 12, iconSize: 14 },
    SM: { h: 36, px: 12, fontSize: 14, iconSize: 16 },
    Base: { h: 40, px: 16, fontSize: 14, iconSize: 18 },
    L: { h: 48, px: 20, fontSize: 16, iconSize: 20 },
    XL: { h: 52, px: 24, fontSize: 16, iconSize: 22 },
};

const CustomButton = ({
    title,
    onPress,
    disabled = false,
    style,
    textStyle,
    iconLeft,
    iconRight,
    size = 'Base',
    variant = 'primary', // primary, secondary, tertiary
    loading = false,
    pressAnimation = 'none' // none | scale
}) => {
    const { theme, typography } = useTheme();
    const config = SIZES[size] || SIZES.Base;
    const pressScale = useRef(new Animated.Value(1)).current;

    const animatePress = (toValue) => {
        if (pressAnimation !== 'scale' || disabled || loading) return;
        Animated.spring(pressScale, {
            toValue,
            useNativeDriver: true,
            speed: 28,
            bounciness: 4,
        }).start();
    };

    const getVariantStyles = (pressed, isDisabled) => {
        if (isDisabled) {
            switch (variant) {
                case 'secondary':
                    return {
                        bg: '#F3F4F6',
                        text: '#99A1AF',
                        stroke: '#E5E7E8',
                        strokeWidth: 1
                    };
                case 'tertiary':
                    return {
                        bg: 'rgba(199, 160, 180, 0.2)', // #C7A0B4 20%
                        text: '#D4006A',
                        stroke: '#C7A0B4',
                        strokeWidth: 1
                    };
                default: // primary
                    return {
                        bg: '#F3F4F6',
                        text: '#99A1AF',
                        stroke: '#E5E7E8',
                        strokeWidth: 1
                    };
            }
        }

        if (pressed) {
            switch (variant) {
                case 'secondary':
                    return {
                        bg: '#F3F4F6',
                        text: '#101828',
                        stroke: '#E5E7EB',
                        strokeWidth: 1,
                        shadow: '#F3F4F6'
                    };
                case 'tertiary':
                    return {
                        bg: 'rgba(255, 0, 128, 0.1)', // #FF0080 10%
                        text: '#D4006A',
                        stroke: '#D4006A',
                        strokeWidth: 1,
                        shadow: '#F3F4F6'
                    };
                default: // primary
                    return {
                        isGradient: true,
                        text: '#FFFFFF',
                        stroke: '#7828CA',
                        strokeWidth: 2,
                        shadow: '#E5E7EB'
                    };
            }
        }

        // Initial State
        switch (variant) {
            case 'secondary':
                return {
                    bg: '#F9FAFB',
                    text: '#4A5565',
                    stroke: '#E5E7EB',
                    strokeWidth: 1
                };
            case 'tertiary':
                return {
                    bg: '#FFFFFF',
                    text: '#FF0080',
                    stroke: '#FF0080',
                    strokeWidth: 1
                };
            default: // primary
                return {
                    isGradient: true,
                    text: '#FFFFFF',
                    stroke: 'transparent',
                    strokeWidth: 0
                };
        }
    };

    return (
        <Animated.View style={[styles.container, style, { transform: [{ scale: pressScale }] }]}>
            <Pressable
                onPress={onPress}
                onPressIn={() => animatePress(0.94)}
                onPressOut={() => animatePress(1)}
                disabled={disabled || loading}
                style={({ pressed }) => {
                    const v = getVariantStyles(pressed, disabled);
                    return [
                        styles.buttonBase,
                        {
                            height: config.h,
                            backgroundColor: v.bg || 'transparent',
                            borderColor: v.stroke,
                            borderWidth: v.strokeWidth,
                        },
                        pressed && !disabled && v.shadow && {
                            ...Platform.select({
                                ios: {
                                    shadowColor: v.shadow,
                                    shadowOffset: { width: 0, height: 1 },
                                    shadowOpacity: 1,
                                    shadowRadius: 2,
                                },
                                android: {
                                    elevation: 4,
                                },
                            })
                        }
                    ];
                }}
            >
                {({ pressed }) => {
                    const v = getVariantStyles(pressed, disabled);
                    const content = (
                        <View style={[styles.contentRow, { paddingHorizontal: config.px }]}>
                            {iconLeft && !loading && (
                                <Ionicons
                                    name={iconLeft}
                                    size={config.iconSize}
                                    color={v.text}
                                    style={styles.iconLeft}
                                />
                            )}
                            {loading ? (
                                <View style={styles.loadingRow}>
                                    <ActivityIndicator size="small" color={v.text} />
                                    <Text style={[
                                        styles.text,
                                        styles.loadingText,
                                        {
                                            fontFamily: typography.medium,
                                            fontSize: config.fontSize,
                                            color: v.text
                                        },
                                        textStyle
                                    ]}>
                                        Procesando...
                                    </Text>
                                </View>
                            ) : (
                                <Text style={[
                                    styles.text,
                                    {
                                        fontFamily: typography.medium,
                                        fontSize: config.fontSize,
                                        color: v.text
                                    },
                                    textStyle
                                ]}>
                                    {title}
                                </Text>
                            )}
                            {iconRight && !loading && (
                                <Ionicons
                                    name={iconRight}
                                    size={config.iconSize}
                                    color={v.text}
                                    style={styles.iconRight}
                                />
                            )}
                        </View>
                    );

                    if (v.isGradient && !disabled) {
                        return (
                            <LinearGradient
                                colors={['#7828CA', '#FF0080']}
                                start={{ x: 0, y: 0 }}
                                end={{ x: 1, y: 1 }}
                                style={styles.gradient}
                            >
                                {pressed && <View style={styles.hoverOverlay} />}
                                {content}
                            </LinearGradient>
                        );
                    }

                    return content;
                }}
            </Pressable>
        </Animated.View>
    );
};

const styles = StyleSheet.create({
    container: {
        borderRadius: 12,
        overflow: 'hidden',
    },
    buttonBase: {
        borderRadius: 12,
        justifyContent: 'center',
        alignItems: 'center',
        width: '100%',
    },
    gradient: {
        flex: 1,
        width: '100%',
        justifyContent: 'center',
        alignItems: 'center',
    },
    hoverOverlay: {
        ...StyleSheet.absoluteFillObject,
        backgroundColor: 'rgba(0, 0, 0, 0.2)',
    },
    contentRow: {
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'center',
    },
    loadingRow: {
        flexDirection: 'row',
        alignItems: 'center',
    },
    loadingText: {
        marginLeft: 8,
    },
    text: {
        letterSpacing: 0.2,
    },
    iconLeft: {
        marginRight: 6,
    },
    iconRight: {
        marginLeft: 6,
    },
});

export default CustomButton;
