//
//  CDDomainObject+Addons.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 30/05/10.
//  Copyright 2010 Jérôme Laheurte. All rights reserved.
//

#import "TaskCoachAppDelegate.h"
#import "CDDomainObject+Addons.h"
#import "i18n.h"

@implementation CDDomainObject (Addons)

- (void)updateStatus:(NSInteger)newStatus
{
	switch ([self.status intValue])
	{
		case STATUS_NEW:
		case STATUS_MODIFIED:
			if (newStatus != STATUS_DELETED)
				newStatus = [self.status intValue];
			break;
		case STATUS_DELETED:
			newStatus = STATUS_DELETED;
			break;
	}

	self.status = [NSNumber numberWithInt:newStatus];
}

- (void)markDirty
{
	[self updateStatus:STATUS_MODIFIED];
}

- (void)delete
{
	if ([self.status intValue] == STATUS_NEW)
	{
		[getManagedObjectContext() deleteObject:self];
	}
	else
	{
		[self updateStatus:STATUS_DELETED];
	}
}

@end
