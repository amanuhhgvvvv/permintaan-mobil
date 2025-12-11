import streamlit as st
import datetime
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials

# --- 1. INISIALISASI DAN KONFIGURASI ---
st.set_page_config(page_title="Permintaan Mobil", layout="centered")

# Data Master
STATUS_CHOICES = ["Karyawan", "Istri", "Anak ke-1", "Anak ke-2", "Anak ke-3"]
TUJUAN_CHOICES = ["Kontrol di RS", "Hospitalisasi", "Pasca rawat inap"]

# Fungsi untuk koneksi ke Google Sheets (Hanya dieksekusi sekali)
@st.cache_resource(ttl=3600)
def connect_gsheets():
    """Menginisialisasi koneksi gspread menggunakan kredensial rahasia Streamlit."""
    try:
        # Mengambil kredensial dari st.secrets
        creds_data = st.secrets["gsheets"]["service_account"]
        creds = Credentials.from_service_account_info(creds_data)
        
        # Otorisasi klien gspread
        client = gspread.authorize(creds)
        
        # Buka spreadsheet berdasarkan URL dari st.secrets
        sheet_url = st.secrets["gsheets"]["sheet_url"]
        spreadsheet = client.open_by_url(sheet_url)
        return spreadsheet.get_worksheet(0) # Mengambil sheet pertama
        
    except Exception as e:
        st.error(f"Gagal terhubung ke Google Sheets. Pastikan file secrets.toml sudah benar. Error: {e}")
        return None

worksheet = connect_gsheets()

# --- 2. TAMPILAN FORMULIR STREAMLIT ---
st.title("🚗 Form Permintaan Penggunaan Mobil")

with st.form(key='permintaan_form'):
    st.header("Detail Pemohon")
    
    nama = st.text_input("Nama Pemohon:", help="Masukkan nama lengkap Anda")
    nik = st.text_input("NIK:", help="Nomor Induk Karyawan/Pegawai")
    departemen = st.text_input("Departemen:")

    status = st.selectbox("Status Pemohon:", options=['Pilih Status'] + STATUS_CHOICES)
    tujuan = st.selectbox("Tujuan Perjalanan:", options=['Pilih Tujuan'] + TUJUAN_CHOICES)

    tanggal = st.date_input(
        "Tanggal Keberangkatan:", 
        datetime.date.today(),
        min_value=datetime.date.today()
    )

    submit_button = st.form_submit_button(label='Ajukan Permintaan')

# --- 3. LOGIKA PEMROSESAN & PENYIMPANAN DATA ---

if submit_button:
    # 3.1. Validasi Input
    if 'Pilih Status' in status or 'Pilih Tujuan' in tujuan or not all([nama, nik, departemen]):
        st.error("❌ Mohon lengkapi semua data formulir dengan benar.")
    elif worksheet is None:
         st.warning("⚠️ Koneksi ke Google Sheets belum berhasil. Data tidak dapat disimpan.")
    else:
        # 3.2. Persiapan Data untuk Penyimpanan
        data_baru = [
            nama,
            nik,
            departemen,
            status,
            tujuan,
            tanggal.strftime('%Y-%m-%d') # Format tanggal standar
        ]
        
        try:
            # 3.3. Penyimpanan Data ke Google Sheets (Append Row)
            worksheet.append_row(data_baru)
            st.success("✅ Permintaan Berhasil Diajukan dan Disimpan ke Google Sheets!")
            
            # Reset form (opsional, tapi baik untuk UX)
            # st.experimental_rerun() 

        except Exception as e:
            st.error(f"Gagal menyimpan data ke Google Sheets. Cek kembali izin berbagi file. Error: {e}")
