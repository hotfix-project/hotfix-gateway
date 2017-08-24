# hotfix-gateway
hotfix gateway

## rest api
* GET /check_update?app_id={id}&version={version}
  * request
    * id: int
    * version: string
  * response
    ```
    {
    "status": "20000112",
    "message": "ok",
    "result": {
        "id": 1,
        "version": "1.1.1",
        "rsa": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC+Rfz/AVaakYbCjUvbCPCnZLSj3aiz2+uyDwgw7o5z1XuBTDA+IHmHuAadoeQpdx359f6g4Vqh6DYy+70iXO4FPQi6Uf/aSoCWUyvbZXmc9TlqlggCOykc8Jm4I586z9b80iQYA4CHG8kNgbTZ5ZNcorPaHR89w1RLj9GlpsEGXCv+nGblIO2ULx7wL+IBJ9M0FXuMZNhTCb0Hsy1C1lgJ36Ru3uHVfL6EF3U/riFiamMvsqOvUWGxfir/QBNSHJ65JgZaghQMhDFSXdhbU4KUfLO2mscjRvlfwTAxkhdTwApn3AOcXc1etIgKZNCdEKcP/7xyDpkIVkHSHq+jMPS7 root@vagrant-172-28-32-101",
        "patch": {
            "released": [
                {
                    "id": 2,
                    "download_url": "http://www.baidu.com/"
                }
            ],
            "deleted": [
                {
                    "id": 1
                }
            ]
            }
        }
    }
    ```
* GET /report_update?patch_id={id}
  * request
    * id: int
  * response
    ```
    {"status": "20000112", "message": "ok"}
    ```

## Client workflow
1. Check update
2. Download patch&Decrypt patch&Verification patch&Apply patch
3. Report update status
