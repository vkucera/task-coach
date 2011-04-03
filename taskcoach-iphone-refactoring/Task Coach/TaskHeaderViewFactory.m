//
//  TaskHeaderViewFactory.m
//  Task Coach
//
//  Created by Jérôme Laheurte on 03/04/11.
//  Copyright 2011 __MyCompanyName__. All rights reserved.
//

#import "TaskHeaderViewFactory.h"

static TaskHeaderViewFactory *_instance = NULL;

@implementation TaskHeaderViewFactory

+ (TaskHeaderViewFactory *)instance
{
    if (!_instance)
        _instance = [[TaskHeaderViewFactory alloc] init];
    return _instance;
}

- (TaskHeaderView *)create
{
    [[NSBundle mainBundle] loadNibNamed:@"TaskHeaderView" owner:self options:nil];
    return [template retain];
}

@end
