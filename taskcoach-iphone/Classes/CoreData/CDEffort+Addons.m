//
//  CDEffort+Addons.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 05/06/10.
//  Copyright 2010 Jérôme Laheurte. All rights reserved.
//

#import "CDEffort+Addons.h"
#import "TaskCoachAppDelegate.h"
#import "CDDomainObject+Addons.h"
#import "Database.h"
#import "Configuration.h"

@implementation CDEffort (Addons)

+ (NSSet *)currentEfforts
{
	NSFetchRequest *request = [[[NSFetchRequest alloc] init] autorelease];
	[request setEntity:[NSEntityDescription entityForName:@"CDEffort" inManagedObjectContext:getManagedObjectContext()]];
	[request setPredicate:[NSPredicate predicateWithFormat:@"status != %d AND ended == NULL AND file=%@",
						   STATUS_DELETED, [Configuration configuration].cdCurrentFile]];

	NSError *error;
	NSArray *result = [getManagedObjectContext() executeFetchRequest:request error:&error];
	if (!result)
	{
		NSLog(@"Error fetching efforts: %@", [error localizedDescription]);
		return nil;
	}

	return [NSSet setWithArray:result];
}

@end
