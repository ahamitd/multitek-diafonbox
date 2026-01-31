# Multitek DiafonBox Home Assistant Entegrasyonu

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

Multitek DiafonBox akıllı kapı kontrol sistemi için Home Assistant custom component.

[English](#english) | [Türkçe](#turkish)

---

## <a name="turkish"></a>🇹🇷 Türkçe

### Özellikler

- 🔐 **Kapı Kontrolü** - Kapıyı Home Assistant üzerinden açabilme
- 🔔 **Zil Bildirimleri** - Apartman girişi ve daire kapısı için ayrı sensörler
- 📷 **Kamera Görüntüleri** - Zil çaldığında çekilen snapshot görüntüleri
- 📊 **İstatistikler** - Arama geçmişi ve zil sayaçları
- 🎯 **Event Desteği** - Automation'lar için event tetikleme

### Kurulum

#### HACS ile (Önerilen)

1. HACS > Integrations > ⋮ (sağ üst) > Custom repositories
2. Repository URL'i ekleyin: `https://github.com/ahamitd/multitek-diafonbox`
3. Category: Integration
4. "Multitek DiafonBox" arayın ve yükleyin
5. Home Assistant'ı yeniden başlatın

#### Manuel Kurulum

1. Bu repository'yi indirin
2. `custom_components/multitek_diafonbox` klasörünü Home Assistant `config/custom_components/` dizinine kopyalayın
3. Home Assistant'ı yeniden başlatın

### Yapılandırma

1. Home Assistant > Ayarlar > Cihazlar ve Servisler
2. "+ Entegrasyon Ekle" butonuna tıklayın
3. "Multitek DiafonBox" arayın
4. E-posta ve şifrenizi girin
5. Kurulum tamamlandı!

### Entity'ler

Entegrasyon aşağıdaki entity'leri oluşturur:

#### Lock (Kilit)
- `lock.{location_name}_kapi` - Kapı açma kontrolü

#### Binary Sensor (İkili Sensör)
- `binary_sensor.{location_name}_apartman_zili` - Apartman girişi zili
- `binary_sensor.{location_name}_daire_zili` - Daire kapısı zili

#### Camera (Kamera)
- `camera.{location_name}_son_zil_goruntusu` - Son zil snapshot'ı

#### Sensor (Sensör)
- `sensor.{location_name}_son_zil_zamani` - Son zil zamanı
- `sensor.{location_name}_bugun_zil_sayisi` - Bugün kaç kez zil çaldı
- `sensor.{location_name}_toplam_arama` - Toplam arama sayısı

### Örnek Automation'lar

#### Zil Çaldığında Bildirim Gönder

```yaml
automation:
  - alias: "Kapı Zili Bildirimi"
    trigger:
      - platform: state
        entity_id: binary_sensor.seran_home_daire_zili
        to: "on"
    action:
      - service: notify.mobile_app_iphone
        data:
          title: "🔔 Kapı Zili"
          message: "Birisi kapınızı çalıyor!"
          data:
            image: "{{ state_attr('camera.seran_home_son_zil_goruntusu', 'entity_picture') }}"
```

#### Event ile Kapı Açma

```yaml
automation:
  - alias: "Zil Çalınca Otomatik Kapı Aç"
    trigger:
      - platform: event
        event_type: multitek_diafonbox_doorbell_pressed
    action:
      - service: lock.unlock
        target:
          entity_id: lock.seran_home_kapi
```

#### Gece Zil Bildirimi

```yaml
automation:
  - alias: "Gece Zil Uyarısı"
    trigger:
      - platform: state
        entity_id: binary_sensor.seran_home_apartman_zili
        to: "on"
    condition:
      - condition: time
        after: "22:00:00"
        before: "07:00:00"
    action:
      - service: notify.all_devices
        data:
          title: "⚠️ Gece Zil"
          message: "Gece saatlerinde zil çalındı!"
          data:
            priority: high
```

### Events

Entegrasyon aşağıdaki event'leri tetikler:

#### `multitek_diafonbox_doorbell_pressed`
Zil çaldığında tetiklenir.

**Event Data:**
```json
{
  "call_id": "abc123",
  "call_from": "2014",
  "call_to": "01001",
  "location_id": "VZG20250517204814978sem",
  "timestamp": "1769696404565",
  "snapshot_path": "/tmp/MULTITEK_CALL_IMAGES/.../snapshot.jpeg"
}
```

#### `multitek_diafonbox_door_opened`
Kapı açıldığında tetiklenir.

**Event Data:**
```json
{
  "location_id": "VZG20250517204814978sem",
  "location_name": "Seran Home",
  "device_sip": "2014"
}
```

### Sorun Giderme

#### Entegrasyon eklenmiyor
- Home Assistant loglarını kontrol edin
- `custom_components/multitek_diafonbox` klasörünün doğru yerde olduğundan emin olun
- Home Assistant'ı yeniden başlatın

#### Kapı açılmıyor
- İnternet bağlantınızı kontrol edin
- Multitek Cloud uygulamasında kapıyı açabildiğinizden emin olun
- Home Assistant loglarında hata mesajlarını kontrol edin

#### Zil bildirimleri gelmiyor
- Binary sensor'ların durumunu kontrol edin
- Polling interval'ı azaltmayı deneyin (varsayılan 30 saniye)

### Destek

Sorun bildirmek veya öneride bulunmak için [GitHub Issues](https://github.com/ahamitd/multitek-diafonbox/issues) kullanın.

---

## <a name="english"></a>🇬🇧 English

### Features

- 🔐 **Door Control** - Open door through Home Assistant
- 🔔 **Doorbell Notifications** - Separate sensors for building entrance and apartment door
- 📷 **Camera Snapshots** - View snapshots taken when doorbell rings
- 📊 **Statistics** - Call history and ring counters
- 🎯 **Event Support** - Event triggers for automations

### Installation

#### HACS (Recommended)

1. HACS > Integrations > ⋮ (top right) > Custom repositories
2. Add repository URL: `https://github.com/ahamitd/multitek-diafonbox`
3. Category: Integration
4. Search for "Multitek DiafonBox" and install
5. Restart Home Assistant

#### Manual Installation

1. Download this repository
2. Copy `custom_components/multitek_diafonbox` folder to Home Assistant `config/custom_components/` directory
3. Restart Home Assistant

### Configuration

1. Home Assistant > Settings > Devices & Services
2. Click "+ Add Integration"
3. Search for "Multitek DiafonBox"
4. Enter your email and password
5. Done!

### Entities

The integration creates the following entities:

#### Lock
- `lock.{location_name}_kapi` - Door control

#### Binary Sensor
- `binary_sensor.{location_name}_apartman_zili` - Building entrance doorbell
- `binary_sensor.{location_name}_daire_zili` - Apartment door doorbell

#### Camera
- `camera.{location_name}_son_zil_goruntusu` - Last doorbell snapshot

#### Sensor
- `sensor.{location_name}_son_zil_zamani` - Last ring time
- `sensor.{location_name}_bugun_zil_sayisi` - Today's ring count
- `sensor.{location_name}_toplam_arama` - Total call count

### Example Automations

See Turkish section above for automation examples.

### Events

See Turkish section above for event details.

### Troubleshooting

See Turkish section above for troubleshooting tips.

### Support

Use [GitHub Issues](https://github.com/ahamitd/multitek-diafonbox/issues) to report problems or suggestions.

---

## Lisans / License

MIT License - Detaylar için LICENSE dosyasına bakın / See LICENSE file for details

## Yazan / Author

[@hamitdurmus](https://github.com/hamitdurmus)
