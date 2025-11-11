import { FontAwesome5, MaterialIcons } from '@expo/vector-icons';
import * as ImagePicker from 'expo-image-picker';
import { useEffect, useRef, useState } from 'react';
import { ActivityIndicator, Alert, Animated, Image, Platform, ScrollView, StyleSheet, Switch, Text, TouchableOpacity, View } from 'react-native';

const BACKEND_URL = "http://192.168.1.116:8000/predict"; 

export default function App() {
    const [imageUri, setImageUri] = useState(null);
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [isDark, setIsDark] = useState(false);
    const imageAnim = useRef(new Animated.Value(0)).current;
    const resultAnim = useRef(new Animated.Value(0)).current;

    const themeStyles = {
        background: isDark ? '#0b1220' : '#f7f9fc',
        card: isDark ? '#101827' : '#ffffff',
        text: isDark ? '#e6eef8' : '#222222',
        subtitle: isDark ? '#9fb3d6' : '#666666',
        primary: isDark ? '#6ec6ff' : '#0b5fff',
        buttonBg: isDark ? '#1e88e5' : '#2196F3',
        predictBg: isDark ? '#1565c0' : '#007ACC'
    };

    useEffect(() => {
        if (imageUri) {
            imageAnim.setValue(0);
            Animated.timing(imageAnim, { toValue: 1, duration: 400, useNativeDriver: true }).start();
        }
    }, [imageUri]);

    useEffect(() => {
        if (result) {
            resultAnim.setValue(0);
            Animated.timing(resultAnim, { toValue: 1, duration: 450, delay: 100, useNativeDriver: true }).start();
        }
    }, [result]);

    const pickImage = async () => {
        const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
        if (status !== 'granted') {
            Alert.alert('Permission required', 'Permission to access media library is required.');
            return;
        }
        const result = await ImagePicker.launchImageLibraryAsync({
            mediaTypes: ImagePicker.MediaTypeOptions.Images,
            quality: 0.8,
        });
        if (!result.canceled && result.assets && result.assets.length > 0) {
            setImageUri(result.assets[0].uri);
            setResult(null);
        }
    };

    const takePhoto = async () => {
        try {
            // Request camera permission via expo API (keeps behavior consistent for iOS/Android)
            const cameraPerm = await ImagePicker.requestCameraPermissionsAsync();
            if (cameraPerm.status !== 'granted') {
                Alert.alert('Permission required', 'Camera permission required.');
                return;
            }

            // On Android, also request media library permission
            if (Platform.OS === 'android') {
                const mediaPerm = await ImagePicker.requestMediaLibraryPermissionsAsync();
                if (mediaPerm.status !== 'granted') {
                    Alert.alert('Notice', 'Media library permission not granted. Saving photos may be limited.');
                }
            }

            let result;
            try {
                result = await ImagePicker.launchCameraAsync({
                    mediaTypes: ImagePicker.MediaTypeOptions.Images,
                    quality: 0.7,
                    exif: false
                });
            } catch (err) {
                console.error('launchCameraAsync failed', err);
                Alert.alert(
                    'Camera Error',
                    Platform.select({
                        android: 'Unable to access camera. Please check your device settings and ensure camera permissions are enabled.',
                        default: 'Unable to open the camera. Try using "Pick an image" instead.'
                    })
                );
                return;
            }

            if (!result.canceled && result.assets && result.assets.length > 0) {
                setImageUri(result.assets[0].uri);
                setResult(null);
            }
        } catch (err) {
            console.error('takePhoto error', err);
            Alert.alert('Error', err?.message || String(err));
        }
    };

    const predict = async () => {
        if (!imageUri) return Alert.alert('No image', 'Pick or take a photo first.');
        setLoading(true);
        setResult(null);
        try {
            const form = new FormData();
            const filename = imageUri.split('/').pop();
            const match = /\.(\w+)$/.exec(filename);
            const type = match ? `image/${match[1]}` : 'image/jpeg';
            // For Android and iOS we need slightly different uri format in some cases; expo handles it.
            form.append('file', { uri: imageUri, name: filename, type });

            const res = await fetch(BACKEND_URL, {
                method: 'POST',
                body: form,
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });

            if (!res.ok) {
                const text = await res.text();
                throw new Error(text || 'Prediction failed');
            }
            const j = await res.json();
            setResult(j);
        } catch (err) {
            Alert.alert('Error', err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <ScrollView style={{ backgroundColor: themeStyles.background }} contentContainerStyle={[styles.container, { backgroundColor: themeStyles.background }] }>
            <View style={[styles.header, { width: '100%', justifyContent: 'space-between' }]}>
                <View>
                    <Text style={[styles.title, { color: themeStyles.primary }]}>Garbage Detection</Text>
                    <Text style={[styles.subtitle, { color: themeStyles.subtitle }]}>Quickly classify common waste types</Text>
                </View>
                <View style={{ flexDirection: 'row', alignItems: 'center' }}>
                    <MaterialIcons name={isDark ? 'nights-stay' : 'wb-sunny'} size={18} color={themeStyles.primary} style={{ marginRight: 8 }} />
                    <Switch value={isDark} onValueChange={setIsDark} />
                </View>
            </View>

            <TouchableOpacity style={[styles.button, { backgroundColor: themeStyles.buttonBg }, loading && styles.buttonDisabled]} onPress={pickImage} activeOpacity={0.8} disabled={loading}>
                <MaterialIcons name="photo-library" size={18} color="#fff" style={{ marginRight: 8 }} />
                <Text style={styles.buttonText}>Pick an image</Text>
            </TouchableOpacity>

            <TouchableOpacity style={[styles.button, { backgroundColor: themeStyles.buttonBg }, loading && styles.buttonDisabled]} onPress={takePhoto} activeOpacity={0.8} disabled={loading}>
                <MaterialIcons name="photo-camera" size={18} color="#fff" style={{ marginRight: 8 }} />
                <Text style={styles.buttonText}>Take a photo</Text>
            </TouchableOpacity>

            {imageUri && (
                <Animated.View style={[styles.imageWrapper, { backgroundColor: themeStyles.card, opacity: imageAnim, transform: [{ translateY: imageAnim.interpolate({ inputRange: [0, 1], outputRange: [20, 0] }) }] }] }>
                    <Image source={{ uri: imageUri }} style={styles.image} resizeMode="cover" />
                </Animated.View>
            )}

            <TouchableOpacity style={[styles.button, { backgroundColor: themeStyles.predictBg }, loading && styles.buttonDisabled]} onPress={predict} disabled={loading} activeOpacity={0.8}>
                <FontAwesome5 name="search" size={16} color="#fff" style={{ marginRight: 8 }} />
                <Text style={styles.buttonText}>Predict</Text>
            </TouchableOpacity>

            {loading && <ActivityIndicator size="large" style={{ marginTop: 10 }} />}

            {result && (
                <Animated.View style={[styles.resultBox, { backgroundColor: themeStyles.card, opacity: resultAnim, transform: [{ translateY: resultAnim.interpolate({ inputRange: [0, 1], outputRange: [12, 0] }) }] }]}>
                    <Text style={[styles.resultTitle, { color: themeStyles.text }]}>Prediction: {result.prediction} ({(result.confidence * 100).toFixed(2)}%)</Text>
                    <Text style={[styles.resultText, { color: themeStyles.text }]}>Latency: {(result.latency * 1000).toFixed(1)} ms</Text>
                    <Text style={[styles.resultText, { color: themeStyles.text, marginTop: 8 }]}>Top results:</Text>
                    {result.top_k && Array.isArray(result.top_k) && result.top_k.length > 0 ? (
                        result.top_k.map((t, i) => (
                            <View key={i} style={styles.topRow}>
                                <MaterialIcons name="label" size={16} color={themeStyles.primary} style={{ marginRight: 8 }} />
                                <Text style={[styles.topItem, { color: themeStyles.text }]}>{i + 1}. {t.class} — {(t.confidence * 100).toFixed(2)}%</Text>
                            </View>
                        ))
                    ) : (
                        <Text style={[styles.resultText, { color: themeStyles.text }]}>No top results available</Text>
                    )}
                </Animated.View>
            )}

            <View style={styles.footer}>
                <Text style={styles.footerText}>Model v1.0 • Built with Expo</Text>
            </View>
        </ScrollView>
    );
}

const styles = StyleSheet.create({
    container: {
        padding: 20,
        alignItems: 'center',
    },
    title: {
        fontSize: 24,
        fontWeight: '700',
        marginBottom: 16,
        color: '#0b5fff',
    },
    header: {
        alignItems: 'center',
        marginBottom: 8,
    },
    subtitle: {
        fontSize: 14,
        color: '#666',
        marginTop: 4,
    },
    button: {
        flexDirection: 'row',
        justifyContent: 'center',
        width: '100%',
        backgroundColor: '#2196F3',
        paddingVertical: 12,
        borderRadius: 8,
        alignItems: 'center',
        marginVertical: 8,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.2,
        shadowRadius: 3,
        elevation: 3,
    },
    predictButton: {
        backgroundColor: '#007ACC',
    },
    buttonText: {
        color: '#fff',
        fontSize: 16,
        fontWeight: '600',
    },
    buttonDisabled: {
        opacity: 0.6,
    },
    imageWrapper: {
        width: '100%',
        height: 360,
        marginTop: 12,
        borderRadius: 12,
        overflow: 'hidden',
        backgroundColor: '#f0f0f0',
    },
    image: {
        width: '100%',
        height: '100%',
    },
    resultBox: {
        width: '100%',
        backgroundColor: '#fff',
        padding: 12,
        borderRadius: 8,
        marginTop: 16,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 1 },
        shadowOpacity: 0.1,
        shadowRadius: 2,
        elevation: 2,
    },
    resultTitle: {
        fontSize: 18,
        fontWeight: '700',
        marginBottom: 6,
    },
    resultText: {
        fontSize: 14,
        color: '#333',
    },
    topItem: {
        fontSize: 14,
        marginTop: 4,
    }
    ,
    topRow: {
        flexDirection: 'row',
        alignItems: 'center',
        marginTop: 6,
    }
    ,
    footer: {
        marginTop: 18,
        paddingVertical: 12,
    },
    footerText: {
        fontSize: 12,
        color: '#888'
    }
});
