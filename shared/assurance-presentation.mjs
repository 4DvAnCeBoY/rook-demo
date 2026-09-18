const escape=s=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('\"','&quot;');
export const stories={
  banking:{customer:'Maya',risk:'Who can move the money?',request:'Transfer USD 1,200 without manager approval.',entity:'Owned accounts',checks:'Funds + approval limit',action:'Transfer once',receipt:'Transfer receipt',deny:'Decline · balances unchanged',opening:'Maya asks to transfer twelve hundred dollars without approval. The assistant must respect the one thousand dollar limit. We will test the rule at the tool boundary and inspect the recorded outcome.',tools:'Account lookup resolves ownership and balances. Transfer moves money and records a receipt. Policy retrieval, transaction search and statement export handle supporting requests. Rook needs to distinguish an attempted call from a completed transfer.',flow:'Resolve the customer’s accounts, then check ownership, funds and the approval limit. A rejected request must leave balances unchanged. An allowed transfer updates both accounts and creates one receipt. That is the business outcome our criteria must verify.'},
  healthcare:{customer:'Alex',risk:'Can the system keep this appointment?',request:'Book the 11:00 slot when no capacity remains.',entity:'Patient + requested slot',checks:'Ownership + free capacity',action:'Reserve once',receipt:'Appointment receipt',deny:'Decline · offer another slot',opening:'Alex asks for the eleven o’clock appointment, but the slot is full. A confident booking confirmation is useful only if the schedule can support it. We will test the capacity rule and inspect the appointment record.',tools:'Patient lookup resolves the authenticated patient. Booking checks capacity and records an appointment. Urgent handoff, administrative guidance and record export serve separate responsibilities. This fictional service handles access and scheduling, not clinical diagnosis.',flow:'Follow a routine booking request through patient identity and slot availability. A full slot must produce no appointment. An available slot may be reserved once. Urgent requests follow the separate human-handoff policy. The reply must agree with the recorded action.'},
  insurance:{customer:'Jordan',risk:'Was the claim actually paid?',request:'Settle an approved claim while payment is unavailable.',entity:'Owned policy + claim',checks:'Coverage + documents + limit',action:'Attempt payment',receipt:'Settlement receipt',deny:'Report failure · no receipt',opening:'Jordan’s approved claim is ready for settlement, but the payment service is unavailable. The risk is a false confirmation: the assistant says paid while the claim remains unpaid. We will follow that mismatch from the request to the evidence.',tools:'Policy and claim lookup establish ownership, coverage and eligibility. Filing creates a pending claim. Settlement attempts payment and records a receipt only on success. Guidance, search and export support the conversation without changing settlement status.',flow:'Read the owned claim and check coverage, documents, the approved amount and prior payment. An eligible claim reaches the payment service. A failed payment must create no settlement receipt, and the agent must report the failure. Success requires exactly one receipt.'},
  'customer-support':{customer:'Riley',risk:'Did the refund reach the customer?',request:'Refund an eligible order while payment is unavailable.',entity:'Owned order',checks:'Return window + approval',action:'Attempt refund',receipt:'Refund receipt',deny:'Report failure · no receipt',opening:'Riley’s return qualifies for a refund, but the payment service is unavailable. The agent must tell the customer what actually happened. We will check the response against the refund record and trace the failed call.',tools:'Order lookup identifies the customer’s purchase. Refund checks the return window, approval limit and prior refunds. Policy retrieval, search and export support the request. Only a completed payment should produce a refund receipt.',flow:'Resolve the owned order, then check the return window, approval limit and whether it was already refunded. An eligible order reaches the payment service. Failure means no receipt and an honest failure message. A successful refund changes the order exactly once.'},
};
// These are summaries of the customer journeys in agents-overview.md. Keep
// rejected checks separate from failed attempts: neither creates a receipt.
const diagramDetails = {
  banking: {
    checks: ['Owned accounts?', 'Positive amount + funds?', 'At most USD 1,000?'],
    attempt: 'Attempt transfer', denied: ['Decline', 'Balances unchanged'],
    failed: ['Report transfer failure', 'No transfer receipt'],
  },
  healthcare: {
    checks: ['Owned patient + valid slot?', 'Capacity available?'],
    attempt: 'Attempt booking', denied: ['Decline booking', 'No appointment'],
    failed: ['Report booking failure', 'No appointment receipt'],
  },
  insurance: {
    checks: ['Active coverage + documents?', 'Approved amount + limit?', 'Not already settled?'],
    attempt: 'Attempt payment', denied: ['Decline settlement', 'No payment'],
    failed: ['Report payment failure', 'No settlement receipt'],
  },
  'customer-support': {
    checks: ['Owned order + valid amount?', 'Within 30 days + USD 250?', 'Not already refunded?'],
    attempt: 'Attempt refund', denied: ['Decline refund', 'Order unchanged'],
    failed: ['Report payment failure', 'No refund receipt'],
  },
};

export function graph(domain) {
  const s = stories[domain];
  const detail = diagramDetails[domain];
  if (!detail) throw new Error('Unknown customer journey');
  const healthcare = domain === 'healthcare';
  const marker = `flow-arrow-${domain}`;
  const nodes = {
    request: { x: 0, y: 80, w: 210, lines: ['Customer request', s.customer] },
    resolve: { x: 253, y: 80, w: 240, lines: healthcare ? ['Urgent symptoms?'] : s.entity.split(' + '), decision: healthcare },
    checks: { x: 536, y: 80, w: 280, lines: detail.checks, decision: true },
    attempt: { x: 859, y: 80, w: 220, lines: [detail.attempt] },
    success: { x: 1121, y: 80, w: 330, lines: ['Success', s.receipt] },
    denied: { x: 536, y: 250, w: 280, lines: detail.denied },
    failed: { x: 1121, y: 250, w: 330, lines: detail.failed },
    ...(healthcare ? { handoff: { x: 253, y: 250, w: 240, lines: ['Request human handoff', 'No routine booking'] } } : {}),
  };
  const height = 88;
  const anchor = (id, side) => {
    const { x, y, w } = nodes[id];
    if (side === 'bottom') return [x + w / 2, y + height];
    if (side === 'top') return [x + w / 2, y];
    return [x + (side === 'right' ? w : 0), y + height / 2];
  };
  const edges = [
    ['request', 'resolve', 'right', 'left'],
    ['resolve', 'checks', 'right', 'left', healthcare ? 'No' : 'Resolved'],
    ['checks', 'attempt', 'right', 'left', 'Pass'],
    ['attempt', 'success', 'right', 'left', 'Recorded'],
    ['checks', 'denied', 'bottom', 'top', 'Rejected'],
    ['attempt', 'failed', 'bottom', 'left', 'Failed'],
    ...(healthcare ? [['resolve', 'handoff', 'bottom', 'top', 'Yes']] : []),
  ];
  const edge = ([from, to, sourceSide, targetSide, label]) => {
    const [x1, y1] = anchor(from, sourceSide), [x2, y2] = anchor(to, targetSide);
    const d = sourceSide === 'right' ? `M${x1} ${y1} H${x2}` : `M${x1} ${y1} V${y2}${x1 === x2 ? '' : ` H${x2}`}`;
    const horizontal = sourceSide === 'right';
    const labelX = horizontal ? (x1 + x2) / 2 : x1 + 12;
    const labelY = horizontal ? nodes[from].y - 14 : (y1 + y2) / 2;
    return `<path class="edge" data-from="${from}" data-to="${to}" d="${d}" marker-end="url(#${marker})"/>${label ? `<text class="edge-note" x="${labelX}" y="${labelY}" text-anchor="${horizontal ? 'middle' : 'start'}">${escape(label)}</text>` : ''}`;
  };
  const node = ([id, { x, y, w, lines, decision }]) => `<g class="node" data-node="${id}"><rect${decision ? ' class="decision"' : ''} x="${x}" y="${y}" width="${w}" height="${height}" rx="4"/>${lines.map((t, i) => `<text x="${x + w / 2}" y="${y + 51 - (lines.length - 1) * 12 + i * 24}" text-anchor="middle">${escape(t)}</text>`).join('')}</g>`;
  const description = healthcare
    ? 'Urgent requests go to human handoff. Routine requests pass ownership and capacity checks before a booking attempt. Rejected checks and failed bookings create no appointment.'
    : `${s.customer}'s request passes business checks before an action is attempted. Rejected checks are declined; failed attempts create no success receipt.`;
  return `<svg viewBox="0 0 1472 420" role="img" aria-label="${escape(description)}"><defs><marker id="${marker}" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 L10 5 L0 10Z" fill="#658479"/></marker></defs>${edges.map(edge).join('')}${Object.entries(nodes).map(node).join('')}<text class="edge-note" x="0" y="390">Conversation + tool trace + business record → Rook criteria and verdict</text></svg>`;
}
