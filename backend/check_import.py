try:
    import youtube_transcript_api
    print("STILL IMPORTABLE:", youtube_transcript_api.__file__)
except ImportError:
    print("Cleanly uninstalled.")
