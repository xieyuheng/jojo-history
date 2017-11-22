(require 'package)
(let* ((no-ssl (and (memq system-type '(windows-nt ms-dos))
                    (not (gnutls-available-p))))
       (url (concat (if no-ssl "http" "https") "://melpa.org/packages/")))
  (add-to-list 'package-archives (cons "melpa" url) t))
(when (< emacs-major-version 24)
  ;; For important compatibility libraries like cl-lib
  (add-to-list 'package-archives '("gnu" . "https://elpa.gnu.org/packages/")))
(package-initialize)

(add-to-list 'load-path "~/.emacs.d/org/lisp/")
(require 'org)



(setq python-indent-guess-indent-offset nil)
(setq python-indent-offset 4)

(defun color-message (.color .string)
  (message
   (concat (char-to-string 27)
           "[" (number-to-string .color) ";1m"
           .string
           (char-to-string 27)
           "[0m")))

(defun org/tangle (.file-name)
  (cond
    ((equal (shell-command (concat "ls " .file-name)) 0)
     (color-message 94 (concat " (org/tangle) " .file-name))
     (find-file .file-name)
     (org-babel-tangle))
    (:else
     (color-message
      96
      (concat "(org/tangle) [not find] " .file-name)))))


(org/tangle "jojo.org")
(org/tangle "core.org")
