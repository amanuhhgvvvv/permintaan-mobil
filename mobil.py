import streamlit as st
import datetime

# 1. Konfigurasi Data Master (Sama seperti Flask, untuk modularitas)
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
        min_value=datetime.date.today() # Minimal hari ini
    )

    # Tombol Submit
    submit_button = st.form_submit_button(label='Ajukan Permintaan')

# 2. Logika Pemrosesan (Setelah Tombol Ditekan)
if submit_button:
    # Validasi Dasar
    if 'Pilih Status' in status or 'Pilih Tujuan' in tujuan or not all([nama, nik, departemen]):
        st.error("Mohon lengkapi semua data formulir dengan benar.")
    else:
        st.success("✅ Permintaan Berhasil Diajukan!")
        
        # Output Logika Profesional (Menampilkan data yang akan disimpan/diproses)
        st.subheader("Ringkasan Data yang Diproses:")
        st.info(f"""
        * **Nama:** {nama}
        * **NIK:** {nik}
        * **Departemen:** {departemen}
        * **Status:** {status}
        * **Tujuan:** {tujuan}
        * **Tanggal:** {tanggal.strftime('%d %B %Y')}
        """)
        
        # --- LOGIKA PROFESIONAL: Penyimpanan Data ---
        # Di sini, Anda akan menambahkan kode untuk menyimpan data ke database (misalnya pandas/csv, atau database SQL).