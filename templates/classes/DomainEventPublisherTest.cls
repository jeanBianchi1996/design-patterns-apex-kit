@IsTest
public class DomainEventPublisherTest {

    public class CountingSubscriber implements DomainEventSubscriber {
        public Integer receivedRecords = 0;
        public void handle(String eventName, List<SObject> records) {
            receivedRecords += records.size();
        }
    }

    private static List<SObject> newAccounts(Integer quantity) {
        List<SObject> accounts = new List<SObject>();
        for (Integer index = 0; index < quantity; index++) {
            accounts.add(new Account(Name = 'Conta ' + index));
        }
        return accounts;
    }

    @IsTest
    static void givenSubscribedEventWhenPublishThenNotifyAllSubscribersInBulk() {
        CountingSubscriber billing = new CountingSubscriber();
        CountingSubscriber logistics = new CountingSubscriber();
        DomainEventPublisher publisher = new DomainEventPublisher()
            .subscribe('OrderApproved', billing)
            .subscribe('OrderApproved', logistics);

        publisher.publish('OrderApproved', newAccounts(3));

        Assert.areEqual(3, billing.receivedRecords);
        Assert.areEqual(3, logistics.receivedRecords);
    }

    @IsTest
    static void givenOtherEventWhenPublishThenDoNotNotify() {
        CountingSubscriber billing = new CountingSubscriber();
        DomainEventPublisher publisher = new DomainEventPublisher().subscribe('OrderApproved', billing);

        publisher.publish('OrderCancelled', newAccounts(2));
        publisher.publish('OrderApproved', new List<SObject>());

        Assert.areEqual(0, billing.receivedRecords);
    }

    @IsTest
    static void givenSubscriberClassNameWhenSubscribeThenResolveByConfiguration() {
        DomainEventPublisher publisher = new DomainEventPublisher()
            .subscribe('OrderApproved', 'DomainEventPublisherTest.CountingSubscriber');

        Assert.areEqual(1, publisher.countSubscribers('OrderApproved'));
    }
}
