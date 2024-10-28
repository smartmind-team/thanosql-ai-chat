-- Speech to text
CREATE or REPLACE FUNCTION stt(file_path TEXT)
RETURNS TEXT AS $$
BEGIN
    RETURN thanosql.predict(
        task := 'automatic-speech-recognition',
        engine := 'thanosql',
        input := file_path,
        model := 'smartmind/whisper-large'
    );
END;
$$ LANGUAGE plpgsql;
