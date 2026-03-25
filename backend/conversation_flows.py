FLOWS = {
    "website": {
        1: {
            "question": "What type of website do you need? (Business / E-commerce / Portfolio)",
            "slot": "website_type"
        },
        2: {
            "question": "Do you need hosting as well? (Yes / No)",
            "slot": "hosting"
        },
        3: {
            "final": (
                "Great! Here’s our complete website development process:\n"
                "1️⃣ Requirement analysis\n"
                "2️⃣ UI/UX design\n"
                "3️⃣ Development\n"
                "4️⃣ Testing\n"
                "5️⃣ Deployment & support\n\n"
                "Our team will contact you shortly."
            )
        }
    }
}
