
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


THREEMA_FILENAME_RE = re.compile(r"threema-(\d{8}-\d{6})-.*jpg")

def _datetime_from_threema_image(filename: str):
    match = THREEMA_FILENAME_RE.match(filename)
    if match:
        date = match.group(1)
        return datetime.datetime.strptime(date, "%Y%m%d-%H%M%S")
    else:
        raise ValueError("Threema Filename not as expected")


def get_datetime_of(filename: str):
    if filename.startswith("IMG_"):
        return _datetime_from_android_image(filename)
    elif filename.startswith("DSC_"):
        return _datetime_from_exif_info(filename)
    elif filename.startswith("threema-"):
        return _datetime_from_threema_image(filename)
    else:
        raise ValueError("Unable to parse date for file {}".format(filename))


def is_datetime_correct(filename: str):
    return not filename.startswith("threema-")


TARGET_FORMAT_RE = re.compile(r"^\d{4}_\d{2}_\d{2}__\d{2}\d{2}\d{2}.*")


def is_target_format(filename: str):
    match = TARGET_FORMAT_RE.match(filename)
    return match is not None


def get_new_name_for(filename: str):
    date = get_datetime_of(filename)
    basename = date.strftime("%Y_%m_%d__%H%M%S")
    marker = "_XXXXX" if not is_datetime_correct(filename) else ""
    extension = os.path.splitext(filename)[1].lower()
    return "{}{}{}".format(basename, marker, extension)


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
