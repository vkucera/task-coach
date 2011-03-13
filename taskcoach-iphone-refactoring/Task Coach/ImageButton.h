//
//  ImageButton.h
//  Task Coach
//
//  Created by Jérôme Laheurte on 12/03/11.
//  Copyright 2011 __MyCompanyName__. All rights reserved.
//

#import <Foundation/Foundation.h>


@interface ImageButton : UIImageView
{
    id target;
    SEL action;
    BOOL isInside;
}

- (void)setTarget:(id)target action:(SEL)action;

@end
