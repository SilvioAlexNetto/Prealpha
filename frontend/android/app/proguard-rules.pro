# =========================
# PROGUARD PARA CAPACITOR + REACT
# =========================

# Mantém todas as classes do Capacitor e plugins
-keep class com.getcapacitor.** { *; }
-keep class com.getcapacitor.plugin.** { *; }

# Mantém classes do AndroidX usadas por Capacitor
-keep class androidx.core.** { *; }
-keep class androidx.appcompat.** { *; }
-keep class androidx.fragment.app.** { *; }

# Mantém classes de Parcelable (necessário para FileProvider e Plugins)
-keep class android.os.Parcelable { *; }

# Mantém classes que usam annotations do Capacitor
-keepclassmembers class * {
    @com.getcapacitor.JSObject *;
    @com.getcapacitor.PluginMethod *;
    @com.getcapacitor.annotation.* *;
}

# Mantém classes e métodos usados pelo React Native / React Web via JS
-keep class com.facebook.react.** { *; }
-keep class com.facebook.hermes.** { *; }

# Mantém os recursos do service worker e manifest
-keep class android.webkit.WebView { *; }
-keep class android.webkit.WebViewClient { *; }

# Evita renomear nomes de métodos de interface usados pelo JS
-keepattributes Signature, *Annotation*, EnclosingMethod, InnerClasses

# Mantém nomes de arquivos de recursos para stacktrace (opcional)
-keepattributes SourceFile,LineNumberTable

# =========================
# PLUGINS COMUNS
# =========================
# Camera, Files, Storage, SplashScreen
-keep class com.getcapacitor.plugin.camera.** { *; }
-keep class com.getcapacitor.plugin.filesystem.** { *; }
-keep class com.getcapacitor.plugin.splashscreen.** { *; }
-keep class com.getcapacitor.plugin.storage.** { *; }

# =========================
# MISC
# =========================
# Evita remover classes que possam ser usadas via reflection
-keep class * implements java.io.Serializable { *; }

# =========================
# FIM
# =========================