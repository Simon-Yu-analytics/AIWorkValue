"""Download author-hosted public assets and verify the recorded snapshot hashes."""
from pathlib import Path
import hashlib,json,urllib.request
ROOT=Path(__file__).resolve().parents[1]


def main():
    manifest=json.loads((ROOT/"data/source-manifest.json").read_text())
    for asset in manifest["assets"]:
        path=ROOT/asset["path"]
        if not path.exists():
            path.parent.mkdir(parents=True,exist_ok=True)
            print("Downloading",path.name,flush=True)
            temporary=path.with_suffix(path.suffix+".part")
            request=urllib.request.Request(asset["url"],headers={"User-Agent":"AIWorkValue educational reanalysis"})
            try:
                with urllib.request.urlopen(request,timeout=180) as source,temporary.open("wb") as destination:
                    while block:=source.read(1024*1024):destination.write(block)
                temporary.replace(path)
            finally:temporary.unlink(missing_ok=True)
        if hashlib.sha256(path.read_bytes()).hexdigest()!=asset["sha256"]:
            raise ValueError("Source differs from the recorded snapshot: "+path.name)
    print("Verified",len(manifest["assets"]),"public source assets. Raw files are not redistributed.")


if __name__=="__main__":main()
