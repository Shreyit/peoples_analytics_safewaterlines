-- Optional macOS verification: export this deck with installed PowerPoint.
-- Arguments: absolute PPTX path, absolute destination PDF path.
on run argv
    set inputPath to item 1 of argv
    set outputPath to item 2 of argv
    with timeout of 45 seconds
        tell application "Microsoft PowerPoint"
            open (POSIX file inputPath)
            set deck to active presentation
            if (name of deck) does not contain "Safewater_Lines_People_Experience" then error "The expected deck is not active."
            save deck in (POSIX file outputPath) as save as PDF
            close deck saving no
        end tell
    end timeout
end run
