from eml_parser import EmlReader


# Read an EML file
with open('email.eml', 'rb') as f:
    email_bytes = f.read()

# Parse the email
reader = EmlReader(email_bytes)

# Extract information
subject = reader.get_subject()
sender = reader.get_from()
date = reader.get_date()
attachments = reader.get_attachments()
text_content = reader.get_message_text()
html_content = reader.get_message_html()

# NEW: Get inline images separately
inline_images = reader.get_inline_images()

print(f"Subject: {subject}")
print(f"From: {sender}")
print(f"Date: {date}")
print(f"Found {len(attachments)} attachments")
print(f"Found {len(inline_images)} inline images")

# write original HTML to file (with CID references)
with open('out/html_content-2-original.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

# Option 1: HTML with inline images as data URLs (embedded)
html_with_data_urls = reader.get_message_html_with_inline_images(use_data_urls=True)
with open('out/html_content-2-with-data-urls.html', 'w', encoding='utf-8') as f:
    f.write(html_with_data_urls)

# Option 2: HTML with inline images saved to files
html_with_file_links = reader.get_message_html_with_inline_images(save_images_to='out/images')
with open('out/html_content-2-with-file-links.html', 'w', encoding='utf-8') as f:
    f.write(html_with_file_links)

# write to file text
with open('out/text_content-2.txt', 'w', encoding='utf-8') as f:
    f.write(text_content)

# Save regular attachments (excluding inline images)
for attachment in attachments:
    filename = attachment['filename'] or 'unnamed_attachment'
    with open(f'out/{filename}', 'wb') as f:
        f.write(attachment['content'])
    print(f"Saved attachment: {filename} ({attachment['filesize']} bytes)")

# Save inline images separately
for image in inline_images:
    filename = image['filename'] or 'unnamed_image.png'
    with open(f'out/inline_{filename}', 'wb') as f:
        f.write(image['content'])
    print(f"Saved inline image: {filename} (CID: {image['content_id']}, {image['filesize']} bytes)")

print("\nFiles created:")
print("- out/html_content-2-original.html (with CID references)")
print("- out/html_content-2-with-data-urls.html (images embedded as data URLs)")
print("- out/html_content-2-with-file-links.html (images saved as files)")
print("- out/text_content-2.txt")
print("- Regular attachments in out/")
print("- Inline images in out/ (prefixed with 'inline_')")
print("- Inline images also saved in out/images/ (referenced by HTML)")

