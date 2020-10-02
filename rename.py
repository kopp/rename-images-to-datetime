
import exifread
import datetime
import re
import os


def _datetime_from_exif_info(filename: str):
    with open(filename, "rb") as imagefile:
        tags = exifread.process_file(imagefile, stop_tag="EXIF DateTimeOriginal")
        exif_date: str = tags["EXIF DateTimeOriginal"]
        return datetime.datetime.strptime(exif_date.values, "%Y:%m:%d %H:%M:%S")


def _datetime_from_android_image(filename: str):
    return datetime.datetime.strptime(filename, "IMG_%Y%m%d_%H%M%S%f.jpg")


def get_datetime_of(filename: str):
    if filename.startswith("IMG_"):
        return _datetime_from_android_image(filename)
    elif filename.startswith("DSC_"):
        return _datetime_from_exif_info(filename)
    else:
        raise ValueError("Unable to parse date for file {}".format(filename))


TARGET_FORMAT_RE = re.compile(r"^\d{4}_\d{2}_\d{2}__\d{2}_\d{2}_\d{2}.*")


def is_target_format(filename: str):
    match = TARGET_FORMAT_RE.match(filename)
    return match is not None


def get_new_name_for(filename: str):
    date = get_datetime_of(filename)
    basename = date.strftime("%Y_%m_%d__%H_%M_%S")
    extension = os.path.splitext(filename)[1].lower()
    return "{}{}".format(basename, extension)


def rename_files(directory: str):
    for filename in os.listdir(directory):
        if is_target_format(filename):
            print("  {}: Bleibt so".format(filename))
        else:
            try:
                newname = get_new_name_for(filename)
                if os.path.exists(newname):
                    raise FileExistsError("File already exists")
                os.rename(filename, newname)
                print("  {} -> {}".format(filename, newname))
            except FileExistsError:
                print("{} -/-> {}: Datei existiert bereits".format(filename, newname))
            except ValueError:
                print("{}: Kein Datum ableitbar".format(filename))
            except:  # noqa: This helps to tool to contunue and to fix the error manually
                print("{}: Unbekannter Fehler :(".format(filename))


if __name__ == "__main__":
    rename_files(".")
