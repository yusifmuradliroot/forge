# forge derin analiz (v1.0.0) — nasıl çalışır, nerede kırılır, v2'de ne var

Bu belge teorik + proplu testlerin sonucudur. Dili bilerek sadedir.

## 1. Boru hattı ne yapar (ispatlı)

`strip → short → crypt → pack` — her adım metin dönüşümü, kod asla çalıştırılmaz.

| Adım | Garanti | Kanıt |
|---|---|---|
| `strip` | yorum siler, string/regex/template'a dokunmaz | fixture + bölme/regex probu (`a/b/2` vs `/ab+c/gi` ayırt edildi) |
| `short` | SADECE bir kez tanımlanmış ismi kısaltır; gölgeleme, property (`o.x`), anahtar (`{x:}`), `new x`, global denenmez | işkence fixture'ı: `alpha` gölgelendi→korundu, `beta` key/property→korundu, regex/string içi sağ |
| `crypt` | uzun stringleri şifreler; kısa/`__*`/directive/anahtar/template sağ | node ile birebir aynı çıktı |
| `pack` | tüm dosyayı blob yapar, `FS:1` etiketi koyar | node `--check` OK |
| runner | etiketi okur → kapı (anti-debug) → çözer → koşturur → siler; bozuk etikette reddeder | yanlış etiket/boş girdi → null, kod çalışmaz |

Uçtan uca: ham JS → `.fs` → runner → **birebir aynı davranış** (68KB gerçek dosyada da).

## 2. Bulunan BUG (sıcak düzeltme gerekli)

**ASCII-dışı içerik pack'te bozuluyor.** Türkçe değişken/yorum-dışı harf veya emoji
(`değişken`, `😀`) pack adımında çöpe dönüşüyor. Sebep: pack her karakteri 2 hex
haneye sığdırmaya çalışıyor, Türkçe/emoji 2 haneye sığmıyor, kayma oluyor.
Çözüm: pack önce UTF-8 bayta çevirmeli, runner `TextDecoder` ile açmalı. Türkçe
içerik kaçınılmaz → v1 "tamam" denmeden bu düzeltilmeli.

## 3. Sınırlar (tasarım gereği, bug değil)

- Runner DÜZ metindir: şifre çözme mantığı okunabilir. Gizlenen içeriktir, algoritma değil.
- Bellek garantisi "elinden gelen": çalıştırma anında düz metin bellekte durur.
  Parça-parça çalıştırma (v2) bunu kapatır.
- `debugger` kapısı hafif: kararlı saldırganı durdurmaz, meraklıyı durdurur.
- Tek statik anahtar: bir dosyanın akışı çözülürse yöntem belli olur (içerik değil).

## 4. v2 iş listesi (öncelikli)

**Sıcak düzeltme (v1 bitmeden):**
1. pack UTF-8 + runner `TextDecoder` (yukarıdaki bug).

**Özellik:**
2. Parçalı IR (`FS:2`): segment + harita, tam metin bellekte hiç durmaz.
3. Bütünlük imzası: runner koşturmadan önce paketi doğrular (kurcalanmış `.fs` çalışmaz).
4. Parça-bağımlı anahtarlar: tek akış çözümü yetmez hale gelir.
5. Gerçek ortam testi: mobil Firefox + Violentmonkey (`Function`, kapı eşiği, hız).
6. Geliştirici modu: 2. aşamayı atlayan okunabilir çıktı (bizim debug için).

**Optimizasyon:**
7. Blob hex→base64 (boyut ~2x → ~1.37x; format bayrağı gerekir).
8. Eşik ayarı: crypt uzunluk sınırı ölçüme göre.

**Ölü kod:**
9. Şu an ölü yok (sıfır rebuild). Eski 0.4.0 history'de durur, sorun değil.

**Diğer işler:**
10. Orbit'e gömme + export hattı + `mustContain` uyumu (paketli `.fs`'de marker gizli →
    orbit önce etiketi görüp açmalı).
11. Doküman rewrite: DESIGN/TUTORIAL/CLI/FAQ v1'e göre yeniden yazılacak (wipe'ta gitti,
    sadece FORMAT.md var).
