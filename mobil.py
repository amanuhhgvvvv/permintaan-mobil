import streamlit as st
import datetime
import gspread # Tambahkan library gspread
import pandas as pd # Tambahkan pandas untuk tampilan data (opsional)
from gspread import Worksheet

# --- KONFIGURASI GOOGLE SHEETS ---
# Ganti dengan nama Spreadsheet dan Worksheet Anda
SPREADSHEET_NAME = "PermintaanMobil"
WORKSHEET_NAME = "PERMINTAAN MOBIL"

# @st.cache_resource memastikan koneksi hanya dibuat sekali per sesi.
@st.cache_resource(ttl=3600)
def get_worksheet() -> Worksheet:
    """Menginisialisasi koneksi gspread menggunakan Streamlit Secrets."""
    try:
        # Mengambil kredensial dari Streamlit Secrets
        credentials_dict = st.secrets["gservice_account"]
        
        # Otorisasi gspread
        gc = gspread.service_account_from_dict(credentials_dict)
        
        # Buka Spreadsheet dan Worksheet target
        sh = gc.open(SPREADSHEET_NAME)
        worksheet = sh.worksheet(WORKSHEET_NAME)
        
        return worksheet
        
    except KeyError:
        # Error jika Streamlit Secrets belum diatur
        st.error("Error: Kunci 'gservice_account' tidak ditemukan di Streamlit Secrets. Mohon atur kredensial Anda.")
        st.stop()
    except gspread.exceptions.SpreadsheetNotFound:
        st.error(f"Error: Spreadsheet dengan nama '{SPREADSHEET_NAME}' tidak ditemukan atau Service Account belum diberi akses.")
        st.stop()
    except Exception as e:
        # Error umum lainnya (misalnya masalah koneksi)
        st.error(f"Gagal menghubungkan ke Google Sheets. Error: {e}")
        st.stop()

# Panggil fungsi koneksi di awal aplikasi
ws = get_worksheet()


# 1. Konfigurasi Data Master
STATUS_CHOICES = [
    "Karyawan", "Istri", "Anak ke-1", "Anak ke-2", "Anak ke-3"
]
TUJUAN_CHOICES = [
    "Kontrol di RS", "Hospitalisasi", "Pasca rawat inap"
]

st.set_page_config(page_title="Permintaan Mobil", layout="centered")

st.title("🚗 Form Permintaan Penggunaan Mobil")

# Menggunakan st.form untuk menangani input dalam satu transaksi
with st.form(key='permintaan_form'):
    st.header("Detail Pemohon")
    
    # Input Teks
    nama = st.text_input("Nama Pemohon:", help="Masukkan nama lengkap Anda")
    nik = st.text_input("NIK:", help="Nomor Induk Karyawan/Pegawai")
    departemen = st.text_input("Departemen:")

    # Dropdown (Selectbox)
    status = st.selectbox("Status Pemohon:", options=['Pilih Status'] + STATUS_CHOICES)
    tujuan = st.selectbox("Tujuan Perjalanan:", options=['Pilih Tujuan'] + TUJUAN_CHOICES)

    # Input Tanggal
    tanggal = st.date_input(
        "Tanggal Keberangkatan:", 
        datetime.date.today(),
        min_value=datetime.date.today()
    )

    # Tombol Submit
    submit_button = st.form_submit_button(label='Ajukan Permintaan')

# 2. Logika Pemrosesan (Setelah Tombol Ditekan)
if submit_button:
    # Validasi Dasar
    if 'Pilih Status' in status or 'Pilih Tujuan' in tujuan or not all([nama, nik, departemen]):
        st.error("❌ Mohon lengkapi semua data formulir dengan benar.")
    else:
        try:
            # --- LOGIKA PENYIMPANAN DATA KE GOOGLE SHEETS ---
            
            # 1. Persiapan Data (Pastikan urutan sesuai dengan kolom di Google Sheet Anda!)
            data_pengajuan = [
                nama,
                nik,
                departemen,
                status,
                tujuan,
                tanggal.strftime('%Y-%m-%d'), # Format tanggal standar
                datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') # Timestamp pengajuan
            ]

            # 2. Penyimpanan Data ke Google Sheets (Append Row)
            ws.append_row(data_pengajuan)
            
            # 3. Pesan Sukses
            st.success("✅ Permintaan Berhasil Diajukan dan Disimpan di Google Sheets!")
            st.balloons()
            
            # Output Ringkasan
            st.subheader("Ringkasan Data yang Diproses:")
            columns = ["Nama", "NIK", "Departemen", "Status", "Tujuan", "Tanggal_Berangkat", "Waktu_Pengajuan"]
            st.dataframe(pd.DataFrame([data_pengajuan], columns=columns))

        except Exception as e:
            st.error(f"Terjadi kesalahan saat menyimpan data ke Google Sheets. Mohon periksa kembali izin Service Account Anda. Error: {e}")
