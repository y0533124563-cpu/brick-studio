// Receives signed payment events from Lemon Squeezy and marks the paying user as Pro.
// Only this server can write users/{uid}.pro; the Firestore rules forbid users from writing it.
const functions = require("firebase-functions/v1");
const admin = require("firebase-admin");
const crypto = require("crypto");

admin.initializeApp();

exports.lemonWebhook = functions.region("europe-west1").https.onRequest(async (req, res) => {
  if (req.method !== "POST") { res.status(405).send("POST only"); return; }

  // 1) Check the signature, so nobody can fake a payment
  const secret = process.env.LS_WEBHOOK_SECRET || "";
  const sig = String(req.get("X-Signature") || "");
  const digest = crypto.createHmac("sha256", secret).update(req.rawBody).digest("hex");
  const ok = secret && sig.length === digest.length &&
    crypto.timingSafeEqual(Buffer.from(sig, "utf8"), Buffer.from(digest, "utf8"));
  if (!ok) { res.status(401).send("bad signature"); return; }

  // 2) Find which user paid (the site passes the user's id into the checkout)
  const body = req.body || {};
  const meta = body.meta || {};
  const event = meta.event_name || "";
  const uid = (meta.custom_data || {}).user_id;
  if (!uid || !/^[A-Za-z0-9]{10,128}$/.test(uid)) { res.status(200).send("ignored"); return; }

  // 3) Save the subscription state
  if (event.startsWith("subscription_") && body.data && body.data.type === "subscriptions") {
    const a = body.data.attributes || {};
    const now = Date.now();
    const ends = a.ends_at ? Date.parse(a.ends_at) : 0;
    const active = ["active", "on_trial", "past_due"].includes(a.status) || (a.status === "cancelled" && ends > now);
    await admin.firestore().doc(`users/${uid}`).set({
      pro: {
        active,
        status: a.status || "",
        renewsAt: a.renews_at || null,
        endsAt: a.ends_at || null,
        subscriptionId: String(body.data.id),
        portal: (a.urls || {}).customer_portal || null,
        testMode: !!a.test_mode,
        updated: now,
      },
    }, { merge: true });
  }
  res.status(200).send("ok");
});
