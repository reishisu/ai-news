<?php
class Ticket {
    public string $status;   // open / closed
    public int $userId;      // 問い合わせた人
    public ?int $ownerId;    // 担当者
    public function close(): void { $this->status = 'closed'; }
}
