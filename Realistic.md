%cd /root
!git clone https://${GITHUB_TOKEN}@github.com/constantlycooking/harry-realistic-repo.git
%cd harry-realistic-repo


# Requirements

!pip install -r requirements.txt
!pip install spaces


# Main

!python app.py --share

