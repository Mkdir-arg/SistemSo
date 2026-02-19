import React from 'react';
import { View, Text, StyleSheet, ScrollView } from 'react-native';
import { useTheme } from '../context/ThemeContext';
import { Ionicons } from '@expo/vector-icons';
import StaggeredItem from '../components/StaggeredItem';

const RECENT_ACTIVITY = [
    { id: '1', user: 'Juana Sierra', action: 'sincronizó evidencias georreferenciadas', time: 'Hace 5 min', icon: 'cloud-done', color: '#7928CA' },
    { id: '2', user: 'Carlos Paez', action: 'registró firma electrónica en acta', time: 'Hace 1 hora', icon: 'create', color: '#2DCE89' },
    { id: '3', user: 'Admin', action: 'actualizó legajo 360 de beneficiario', time: 'Hace 3 horas', icon: 'people', color: '#FF0080' },
];

export default function ActivityScreen() {
    const { theme, typography } = useTheme();

    return (
        <ScrollView style={[styles.container, { backgroundColor: theme.colors.background }]} contentContainerStyle={styles.content}>
            <StaggeredItem index={0}>
                <Text style={[styles.sectionTitle, { color: theme.colors.text, fontFamily: typography.bold }]}>
                    Actividad Reciente
                </Text>
            </StaggeredItem>

            <View style={styles.timeline}>
                {RECENT_ACTIVITY.map((item, index) => (
                    <StaggeredItem key={item.id} index={index + 1}>
                        <View style={styles.itemContainer}>
                            <View style={styles.iconColumn}>
                                <View style={[styles.iconWrapper, { backgroundColor: item.color }]}>
                                    <Ionicons name={item.icon} size={18} color="#FFF" />
                                </View>
                                {index < RECENT_ACTIVITY.length - 1 && <View style={[styles.line, { backgroundColor: theme.colors.border }]} />}
                            </View>

                            <View style={styles.textColumn}>
                                <Text style={[styles.itemText, { color: theme.colors.text, fontFamily: typography.medium }]}>
                                    <Text style={{ fontFamily: typography.bold }}>{item.user}</Text> {item.action}
                                </Text>
                                <Text style={[styles.timeText, { color: theme.colors.textSoft, fontFamily: typography.regular }]}>{item.time}</Text>
                            </View>
                        </View>
                    </StaggeredItem>
                ))}
            </View>
        </ScrollView>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
    },
    content: {
        padding: 20,
    },
    sectionTitle: {
        fontSize: 20,
        marginBottom: 24,
    },
    timeline: {
        paddingLeft: 4,
    },
    itemContainer: {
        flexDirection: 'row',
        height: 80,
    },
    iconColumn: {
        alignItems: 'center',
        marginRight: 16,
    },
    iconWrapper: {
        width: 36,
        height: 36,
        borderRadius: 18,
        justifyContent: 'center',
        alignItems: 'center',
        zIndex: 1,
    },
    line: {
        width: 2,
        flex: 1,
    },
    textColumn: {
        paddingTop: 4,
    },
    itemText: {
        fontSize: 15,
        marginBottom: 4,
    },
    timeText: {
        fontSize: 12,
    },
});
