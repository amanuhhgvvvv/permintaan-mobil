import streamlit as st
import datetime
import gspread
import pandas as pd
from gspread import Worksheet
from google.oauth2.service_account import Credentials # <-- IMPORT INI

# --- KONFIGURASI GOOGLE SHEETS ---
# SPREADSHEET_NAME telah dikoreksi di sesi sebelumnya berdasarkan analisis gambar
SPREADSHEET_NAME = "permintaan mobil" # Asumsi Anda sudah mengkoreksi ini di repository Anda
WORKSHEET_NAME = "PERMINTAAN MOBIL"

# --- GOOGLE SHEETS CLIENT/KONEKSI ---
# (Fungsi get_gspread_client() tidak berubah)
@st.cache_resource(ttl=3600)
def get_gspread_client():
    """Menginisialisasi koneksi gspread menggunakan stremlite secrets (kunci global)."""
    try:
        # PENTING: Mengambil setiap kunci secrets secara individual (metode kode lama Anda)
        creds_info = {
            "type": "service_account",
            "project_id": st.secrets["project_id"],
            "private_key_id": st.secrets["private_key_id"],
            "private_key": st.secrets["private_key"],
            "client_email": st.secrets["client_email"],
            "client_id": st.secrets["client_id"],
            # Kunci-kunci tambahan yang sering hilang namun penting untuk autentikasi gspread
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": st.secrets["client_x509_cert_url"]
        }
        
        # Otorisasi menggunakan credentials dari google.oauth2
        credentials = Credentials.from_service_account_info(
            creds_info,
            scopes=["https://www.googleapis.com/auth/spreadsheets"]
        )
        return gspread.authorize(credentials)
        
    except KeyError as e:
        st.error(f"Error Konfigurasi Secrets: Kunci '{e}' tidak ditemukan di Streamlit Secrets. Pastikan semua kunci Service Account ada di Secrets sebagai kunci global (tanpa header [section]).")
        st.stop()
    except Exception as e:
        st.error(f"Gagal menginisialisasi koneksi Google Sheets. Error: {e}")
        st.stop()

# (Fungsi get_worksheet() tidak berubah)
@st.cache_resource(ttl=3600)
def get_worksheet() -> Worksheet:
    """Mendapatkan objek worksheet yang akan digunakan untuk read/write."""
    try:
        gc = get_gspread_client()
        
        # Menggunakan SHEET_ID dari secrets jika Anda menyimpannya di sana
        SHEET_ID = st.secrets.get("SHEET_ID") 
        if not SHEET_ID:
             # Jika tidak ada SHEET_ID, gunakan nama spreadsheet (kurang direkomendasikan)
             sh = gc.open(SPREADSHEET_NAME) 
        else:
             sh = gc.open_by_key(SHEET_ID)

        worksheet = sh.worksheet(WORKSHEET_NAME)
        return worksheet
        
    except gspread.exceptions.SpreadsheetNotFound:
        st.error(f"Error: Spreadsheet '{SPREADSHEET_NAME}' tidak ditemukan atau Service Account belum diberi akses.")
        st.stop()
    except Exception as e:
        st.error(f"Gagal membuka Spreadsheet. Error: {e}")
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
    # --- START REVISI TANGGAL ---
    tanggal = st.date_input(
        "Tanggal Keberangkatan:", 
        datetime.date.today(),
        # min_value=datetime.date.today() <-- BARIS INI DIHAPUS (memperbaiki masalah tanggal mundur)
    )
    # --- END REVISI TANGGAL ---

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
                tanggal.strftime('%Y-%m-%d'), 
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
            st.error(f"Terjadi kesalahan saat menyimpan data ke Google Sheets. Error: {e}")

