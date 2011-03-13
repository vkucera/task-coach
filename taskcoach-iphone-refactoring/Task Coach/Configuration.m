//
//  Configuration.m
//  Task Coach
//
//  Created by Jérôme Laheurte on 13/03/11.
//  Copyright 2011 __MyCompanyName__. All rights reserved.
//

#import "Configuration.h"
#import "Task_CoachAppDelegate.h"

static Configuration *_instance = NULL;

static NSString *kCurrentListConfigName = @"currentList";

/*
static NSString *kSectionsConfigName = @"sections";

@implementation TaskStatusSection

@synthesize condition, displayed;

- (id)initWithCondition:(NSString *)cond
{
    if ((self = [super init]))
    {
        condition = [cond copy];
        displayed = YES;
    }

    return self;
}

@end
*/

@implementation Configuration

// @synthesize sections;

- (id)init
{
    if ((self = [super init]))
    {
		NSUserDefaults *config = [NSUserDefaults standardUserDefaults];

        currentListURL = [config URLForKey:kCurrentListConfigName];

        /*
        if ([config objectForKey:kSectionsConfigName])
        {
            // XXXTODO
        }
        else
        {
            // XXXTODO
        }
         */
    }

    return self;
}

+ (Configuration *)instance
{
    if (!_instance)
        _instance = [[Configuration alloc] init];
    return _instance;
}

- (void)save
{
    NSUserDefaults *config = [NSUserDefaults standardUserDefaults];
    [config setURL:currentListURL forKey:kCurrentListConfigName];
    [config synchronize];
}

#pragma mark - Properties

- (CDList *)currentList
{
    if (!currentListURL)
        return nil;

    return (CDList *)[getPersistentStoreCoordinator() managedObjectIDForURIRepresentation:currentListURL];
}

- (void)setCurrentList:(CDList *)currentList
{
    [currentListURL release];
    currentListURL = [[[currentList objectID] URIRepresentation] copy];
}

@end
