//
//  TaskCellFactory.m
//  Task Coach
//
//  Created by Jérôme Laheurte on 03/04/11.
//  Copyright 2011 __MyCompanyName__. All rights reserved.
//

#import "TaskCellFactory.h"

static TaskCellFactory *_instance = NULL;

@implementation TaskCellFactory

+ (TaskCellFactory *)instance
{
    if (!_instance)
        _instance = [[TaskCellFactory alloc] init];
    return _instance;
}

- (TaskCell *)create
{
    if (UI_USER_INTERFACE_IDIOM() == UIUserInterfaceIdiomPhone)
    {
        [[NSBundle mainBundle] loadNibNamed:@"TaskCell-iPhone" owner:self options:nil];
    }
    else
    {
        // XXXTODO
    }

    return template;
}

- (TaskDetailsCell *)createDetails
{
    if (UI_USER_INTERFACE_IDIOM() == UIUserInterfaceIdiomPhone)
    {
        [[NSBundle mainBundle] loadNibNamed:@"TaskDetailsCell-iPhone" owner:self options:nil];
    }
    else
    {
        // XXXTODO
    }
    
    return detailsTemplate;
}

@end
