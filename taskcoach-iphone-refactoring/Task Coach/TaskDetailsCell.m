//
//  TaskDetailsCell.m
//  Task Coach
//
//  Created by Jérôme Laheurte on 09/04/11.
//  Copyright 2011 __MyCompanyName__. All rights reserved.
//

#import "TaskDetailsCell.h"
#import "CDTask+Addons.h"
#import "i18n.h"

static UIImage *_imageChecked = NULL;
static UIImage *_imageUnchecked = NULL;

@implementation TaskDetailsCell

- (void)dealloc
{
    if (callback)
        Block_release(callback);

    [super dealloc];
}

- (void)setTask:(CDTask *)task callback:(void (^)(id))theCallback
{
    if (!_imageChecked)
    {
        _imageChecked = [[UIImage imageNamed:@"checked"] retain];
        _imageUnchecked = [[UIImage imageNamed:@"unchecked"] retain];
    }

    if (callback)
        Block_release(callback);
    callback = Block_copy(theCallback);

    [doneButton setTitle:_("Done") forState:UIControlStateNormal];
    [doneButton setBackgroundImage:[[UIImage imageNamed:@"blueButton"] stretchableImageWithLeftCapWidth:12.0 topCapHeight:0.0] forState:UIControlStateNormal];
    [doneButton setBackgroundImage:[[UIImage imageNamed:@"whiteButton"] stretchableImageWithLeftCapWidth:12.0 topCapHeight:0.0] forState:UIControlStateHighlighted];
    [doneButton setCallback:callback];

    subject.text = task.name;
    completionButton.image = ([task completionDate]) ? _imageChecked : _imageUnchecked;
    [completionButton setCallback:^(id sender) {
        [task toggleCompletion];
    }];

    if ([task currentEffort])
    {
        [trackButton setTitle:_("Stop tracking") forState:UIControlStateNormal];
    }
    else
    {
        [trackButton setTitle:_("Start tracking") forState:UIControlStateNormal];
    }
    [trackButton setBackgroundImage:[[UIImage imageNamed:@"redButton"] stretchableImageWithLeftCapWidth:12.0 topCapHeight:0.0] forState:UIControlStateNormal];
    [trackButton setBackgroundImage:[[UIImage imageNamed:@"whiteButton"] stretchableImageWithLeftCapWidth:12.0 topCapHeight:0.0] forState:UIControlStateHighlighted];

    [trackButton setCallback:^(id sender) {
        if ([task currentEffort])
            [task stopTracking];
        else
            [task startTracking];
    }];
}

@end
