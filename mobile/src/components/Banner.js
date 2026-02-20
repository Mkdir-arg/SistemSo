import { View, Text, StyleSheet, Platform, Dimensions, Pressable, ImageBackground, TouchableOpacity } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../context/ThemeContext';

const { width } = Dimensions.get('window');
const lightBannerImage = require('../../assets/images/back_banner.jpg');

export default function Banner({
    title,
    syncStatus = 'synced',
    syncPendingCount = 0,
    onSyncPress,
    showBackButton = false,
    onBackPress,
}) {
    const { theme, typography, isDark } = useTheme();
    const isSynced = syncStatus === 'synced';
    const isSyncing = syncStatus === 'syncing';

    return (
        <View style={styles.shadowContainer}>
            <ImageBackground
                source={lightBannerImage}
                style={styles.container}
                imageStyle={{ opacity: 1 }}
                resizeMode="cover"
            >
                <SafeAreaView>
                    <View style={styles.content}>
                        <View style={styles.headerRow}>
                            <View style={styles.leftHeaderGroup}>
                                {showBackButton ? (
                                    <TouchableOpacity onPress={onBackPress} style={styles.backBtn}>
                                        <Ionicons name="chevron-back" size={22} color="#FFF" />
                                    </TouchableOpacity>
                                ) : null}
                                <Text style={[styles.title, { color: '#FFF', fontFamily: typography.extrabold }]}>
                                    {title.toUpperCase()}
                                </Text>
                            </View>

                            <View style={styles.iconGroup}>
                                <Pressable style={styles.iconButton} onPress={onSyncPress}>
                                    <Ionicons
                                        name={isSyncing ? 'sync' : (isSynced ? 'cloud-done' : 'cloud-upload')}
                                        size={28}
                                        color={isSyncing ? '#08B8CC' : (isSynced ? '#2DCE89' : '#FFB020')}
                                    />
                                    {syncPendingCount > 0 ? (
                                        <View style={[styles.syncBadge, { borderColor: '#FFF' }]}>
                                            <Text style={[styles.syncBadgeText, { fontFamily: typography.bold }]}>
                                                {syncPendingCount > 99 ? '99+' : syncPendingCount}
                                            </Text>
                                        </View>
                                    ) : null}
                                </Pressable>

                                <Pressable style={styles.notificationContainer}>
                                    <Ionicons name="notifications-outline" size={26} color="#FFF" />
                                    <View style={[
                                        styles.badge,
                                        {
                                            borderColor: '#FFF'
                                        }
                                    ]}>
                                        <Text style={[styles.badgeText, { fontFamily: typography.bold }]}>2</Text>
                                    </View>
                                </Pressable>
                            </View>
                        </View>
                    </View>
                </SafeAreaView>
            </ImageBackground>
        </View>
    );
}

const styles = StyleSheet.create({
    shadowContainer: {
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 8 },
        shadowOpacity: 0.2,
        shadowRadius: 10,
        elevation: 10,
        zIndex: 10,
    },
    container: {
        paddingTop: Platform.OS === 'android' ? 40 : 10,
        paddingBottom: 25,
        borderBottomLeftRadius: 24,
        borderBottomRightRadius: 24,
        overflow: 'hidden',
    },
    content: {
        paddingHorizontal: 24,
    },
    headerRow: {
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'space-between',
    },
    leftHeaderGroup: {
        flexDirection: 'row',
        alignItems: 'center',
        flexShrink: 1,
    },
    backBtn: {
        width: 30,
        height: 30,
        borderRadius: 15,
        backgroundColor: 'rgba(0,0,0,0.2)',
        alignItems: 'center',
        justifyContent: 'center',
        marginRight: 10,
    },
    title: {
        fontSize: 22,
        letterSpacing: 4,
        textShadowColor: 'rgba(0, 0, 0, 0.1)',
        textShadowOffset: { width: 0, height: 2 },
        textShadowRadius: 4,
    },
    notificationContainer: {
        position: 'relative',
        padding: 4,
    },
    iconGroup: {
        flexDirection: 'row',
        alignItems: 'center',
    },
    iconButton: {
        padding: 4,
        marginRight: 8,
        position: 'relative',
    },
    syncBadge: {
        position: 'absolute',
        top: -2,
        right: -4,
        backgroundColor: '#FF0080',
        minWidth: 16,
        height: 16,
        borderRadius: 8,
        justifyContent: 'center',
        alignItems: 'center',
        borderWidth: 1.5,
        paddingHorizontal: 3,
    },
    syncBadgeText: {
        color: '#FFF',
        fontSize: 9,
        lineHeight: 10,
    },
    badge: {
        position: 'absolute',
        top: 0,
        right: 0,
        backgroundColor: '#FF0080',
        minWidth: 18,
        height: 18,
        borderRadius: 9,
        justifyContent: 'center',
        alignItems: 'center',
        borderWidth: 1.5,
    },
    badgeText: {
        color: '#FFF',
        fontSize: 10,
        textAlign: 'center',
    },
});
