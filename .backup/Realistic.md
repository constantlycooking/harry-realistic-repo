%cd /root
!rm -rf harry-realistic-repo
!git clone https://${GITHUB_TOKEN}@github.com/constantlycooking/harry-realistic-repo.git

%cd harry-realistic-repo

%uv pip install -r requirements.txt

!python app.py --share